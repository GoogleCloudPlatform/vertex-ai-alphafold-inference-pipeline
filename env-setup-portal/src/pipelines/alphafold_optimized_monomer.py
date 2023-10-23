# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Monomer-optimized Alphafold Inference Pipeline."""

from google_cloud_pipeline_components.v1.custom_job import create_custom_training_job_from_component
from kfp.v2 import dsl
from src import config
from src.components import aggregate_features as AggregateOp
from src.components import configure_run as ConfigureRunOp
from src.components import hhblits
from src.components import hhsearch
from src.components import jackhmmer
from src.components import predict as PredictOp
from src.components import relax as RelaxOp


JackhmmerOp = create_custom_training_job_from_component(
    jackhmmer,
    display_name='Jackhmmer',
    machine_type=config.JACKHMMER_MACHINE_TYPE,
    nfs_mounts=[dict(
        server=config.NFS_SERVER,
        path=config.NFS_PATH,
        mountPoint=config.NFS_MOUNT_POINT)],
    network=config.NETWORK
)

HHblitsOp = create_custom_training_job_from_component(
    hhblits,
    display_name='HHblits',
    machine_type=config.HHBLITS_MACHINE_TYPE,
    nfs_mounts=[dict(
        server=config.NFS_SERVER,
        path=config.NFS_PATH,
        mountPoint=config.NFS_MOUNT_POINT)],
    network=config.NETWORK
)

HHsearchOp = create_custom_training_job_from_component(
    hhsearch,
    display_name='HHsearch',
    machine_type=config.HHSEARCH_MACHINE_TYPE,
    nfs_mounts=[dict(
        server=config.NFS_SERVER,
        path=config.NFS_PATH,
        mountPoint=config.NFS_MOUNT_POINT)],
    network=config.NETWORK
)

JobPredictOp = create_custom_training_job_from_component(
    PredictOp,
    display_name = 'Predict',
    machine_type = config.PREDICT_MACHINE_TYPE,
    accelerator_type = config.PREDICT_ACCELERATOR_TYPE,
    accelerator_count = config.PREDICT_ACCELERATOR_COUNT
)

JobRelaxOp = create_custom_training_job_from_component(
    RelaxOp,
    display_name = 'Relax',
    machine_type = config.RELAX_MACHINE_TYPE,
    accelerator_type = config.RELAX_ACCELERATOR_TYPE,
    accelerator_count = config.RELAX_ACCELERATOR_COUNT
)


@dsl.pipeline(
    name='alphafold-monomer-optimized',
    description='AlphaFold monomer inference using parallized MSA search.'
)
def alphafold_monomer_pipeline(
    sequence_path: str,
    project: str,
    region: str,
    max_template_date: str,
    uniref_max_hits: int = config.UNIREF_MAX_HITS,
    mgnify_max_hits: int = config.MGNIFY_MAX_HITS,
    is_run_relax: str = 'relax'
):
  """Monomer-optimized Alphafold Inference Pipeline."""
  run_config = ConfigureRunOp(
      sequence_path=sequence_path,
      model_preset='monomer',
  ).set_display_name('Configure Pipeline Run')

  model_parameters = dsl.importer(
      artifact_uri=config.MODEL_PARAMS_GCS_LOCATION,
      artifact_class=dsl.Artifact,
      reimport=True)
  model_parameters.set_display_name('Model parameters')

  reference_databases = dsl.importer(
      artifact_uri=config.NFS_MOUNT_POINT,
      artifact_class=dsl.Dataset,
      reimport=False,
      metadata={
          'uniref90': config.UNIREF90_PATH,
          'mgnify': config.MGNIFY_PATH,
          'bfd': config.BFD_PATH,
          'small_bfd': config.SMALL_BFD_PATH,
          'uniref30': config.UNIREF30_PATH,
          'pdb70': config.PDB70_PATH,
          'pdb_mmcif': config.PDB_MMCIF_PATH,
          'pdb_obsolete': config.PDB_OBSOLETE_PATH,
          'pdb_seqres': config.PDB_SEQRES_PATH,
          'uniprot': config.UNIPROT_PATH,
          }
  ).set_display_name('Reference databases')

  search_uniref = JackhmmerOp(
      project=project,
      location=region,
      database='uniref90',
      ref_databases=reference_databases.output,
      sequence=run_config.outputs['sequence'],
      maxseq=uniref_max_hits,
  )
  search_uniref.set_display_name('Search Uniref')

  search_mgnify = JackhmmerOp(
      project=project,
      location=region,
      database='mgnify',
      ref_databases=reference_databases.output,
      sequence=run_config.outputs['sequence'],
      maxseq=mgnify_max_hits
  )
  search_mgnify.set_display_name('Search Mgnify')

  search_uniclust = HHblitsOp(
      project=project,
      location=region,
      databases=['uniref30'],
      ref_databases=reference_databases.output,
      sequence=run_config.outputs['sequence'],
  )
  search_uniclust.set_display_name('Search Uniclust')

  search_bfd = HHblitsOp(
      project=project,
      location=region,
      databases=['bfd'],
      ref_databases=reference_databases.output,
      sequence=run_config.outputs['sequence'],
  )
  search_bfd.set_display_name('Search BFD')

  search_pdb = HHsearchOp(
      project=project,
      location=region,
      template_dbs=['pdb70'],
      mmcif_db='pdb_mmcif',
      obsolete_db='pdb_obsolete',
      max_template_date=max_template_date,
      ref_databases=reference_databases.output,
      sequence=run_config.outputs['sequence'],
      msa=search_uniref.outputs['msa'],
  )
  search_pdb.set_display_name('Search Pdb')

  aggregate_features = AggregateOp(
      sequence=run_config.outputs['sequence'],
      msa1=search_uniref.outputs['msa'],
      msa2=search_mgnify.outputs['msa'],
      msa3=search_bfd.outputs['msa'],
      msa4=search_uniclust.outputs['msa'],
      template_features=search_pdb.outputs['template_features'],
  )
  aggregate_features.set_display_name('Aggregate features')

  with dsl.ParallelFor(run_config.outputs['model_runners']) as model_runner:
    model_predict = JobPredictOp(
        project=project,
        location=region,
        model_features=aggregate_features.outputs['features'],
        model_params=model_parameters.output,
        model_name=model_runner.model_name,
        prediction_index=model_runner.prediction_index,
        run_multimer_system=run_config.outputs['run_multimer_system'],
        num_ensemble=run_config.outputs['num_ensemble'],
        random_seed=model_runner.random_seed,
        tf_force_unified_memory=config.TF_FORCE_UNIFIED_MEMORY,
        xla_python_client_mem_fraction=config.XLA_PYTHON_CLIENT_MEM_FRACTION
    )
    model_predict.set_display_name('Predict')

    with dsl.Condition(is_run_relax == 'relax'):
      relax_protein = JobRelaxOp(
        project=project,
        location=region,
        unrelaxed_protein=model_predict.outputs['unrelaxed_protein'],
        use_gpu=True,
        tf_force_unified_memory=config.TF_FORCE_UNIFIED_MEMORY,
        xla_python_client_mem_fraction=config.XLA_PYTHON_CLIENT_MEM_FRACTION
      )
      relax_protein.set_display_name('Relax protein')
