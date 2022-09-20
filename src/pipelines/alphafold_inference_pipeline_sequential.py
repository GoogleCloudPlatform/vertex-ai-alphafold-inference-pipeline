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

"""Sequential Alphafold Inference Pipeline."""

from google_cloud_pipeline_components.v1.custom_job import create_custom_training_job_from_component
from kfp.v2 import dsl
from src import config
from src.components import configure_run as ConfigureRunOp
from src.components import data_pipeline
from src.components import predict_relax as PredictRelaxOp

DataPipelineOp = create_custom_training_job_from_component(
    data_pipeline,
    display_name='Data Pipeline',
    machine_type=config.DATA_PIPELINE_MACHINE_TYPE,
    nfs_mounts=[dict(
        server=config.NFS_SERVER,
        path=config.NFS_PATH,
        mountPoint=config.NFS_MOUNT_POINT)],
    network=config.NETWORK
)


@dsl.pipeline(
    name='alphafold-inference-pipeline',
    description='AlphaFold inference using original data pipeline.'
)
def inference_pipeline(
    sequence_path: str,
    project: str,
    region: str,
    max_template_date: str,
    model_preset: str = 'monomer',
    use_small_bfd: bool = True,
    num_multimer_predictions_per_model: int = 5,
    is_run_relax: bool = True,
):
    """Universal Alphafold Inference Pipeline."""
    run_config = ConfigureRunOp(
        sequence_path=sequence_path,
        model_preset=model_preset,
        num_multimer_predictions_per_model=num_multimer_predictions_per_model,
    ).set_display_name('Configure Pipeline Run')

    model_parameters = dsl.importer(
        artifact_uri=config.MODEL_PARAMS_GCS_LOCATION,
        artifact_class=dsl.Artifact,
        reimport=True
    ).set_display_name('Model parameters')

    reference_databases = dsl.importer(
        artifact_uri=config.NFS_MOUNT_POINT,
        artifact_class=dsl.Dataset,
        reimport=False,
        metadata={
            'uniref90': config.UNIREF90_PATH,
            'mgnify': config.MGNIFY_PATH,
            'bfd': config.BFD_PATH,
            'small_bfd': config.SMALL_BFD_PATH,
            'uniclust30': config.UNICLUST30_PATH,
            'pdb70': config.PDB70_PATH,
            'pdb_mmcif': config.PDB_MMCIF_PATH,
            'pdb_obsolete': config.PDB_OBSOLETE_PATH,
            'pdb_seqres': config.PDB_SEQRES_PATH,
            'uniprot': config.UNIPROT_PATH,
        }
    ).set_display_name('Reference databases')

    data_pipeline = DataPipelineOp(
        project=project,
        location=region,
        ref_databases=reference_databases.output,
        sequence=run_config.outputs['sequence'],
        max_template_date=max_template_date,
        run_multimer_system=run_config.outputs['run_multimer_system'],
        use_small_bfd=use_small_bfd,
    ).set_display_name('Prepare Features')

    model_predict_relax = PredictRelaxOp(
        model_features=data_pipeline.outputs['features'],
        model_params=model_parameters.output,
        prediction_runners=run_config.outputs['model_runners'],
        run_multimer_system=run_config.outputs['run_multimer_system'],
        num_ensemble=run_config.outputs['num_ensemble'],
        run_relax=is_run_relax,
    ).set_display_name('Predict/Relax')
    model_predict_relax.set_cpu_limit(config.CPU_LIMIT)
    model_predict_relax.set_memory_limit(config.MEMORY_LIMIT)
    model_predict_relax.set_gpu_limit(config.GPU_LIMIT)
    model_predict_relax.add_node_selector_constraint(
        config.GKE_ACCELERATOR_KEY, config.GPU_TYPE)
    model_predict_relax.set_env_variable(
        'TF_FORCE_UNIFIED_MEMORY', config.TF_FORCE_UNIFIED_MEMORY)
    model_predict_relax.set_env_variable(
        'XLA_PYTHON_CLIENT_MEM_FRACTION',
        config.XLA_PYTHON_CLIENT_MEM_FRACTION)
