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
import sys
sys.path.append('..')

import config
from components import configure_run as ConfigureRunOp
from components import data_pipeline
from components import predict_relax as PredictRelaxOp

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

JobPredictRelaxOp = create_custom_training_job_from_component(
    PredictRelaxOp,
    display_name = 'Predict/Relax',
    machine_type = config.PREDICT_MACHINE_TYPE,
    accelerator_type = config.PREDICT_ACCELERATOR_TYPE,
    accelerator_count = config.PREDICT_ACCELERATOR_COUNT
)


@dsl.pipeline(
    name='alphafold-inference-pipeline',
    description='AlphaFold inference using original data pipeline and sequential prediction and relaxation.'
)
def alphafold_inference_pipeline_seq(
    sequence_path: str,
    project: str,
    region: str,
    max_template_date: str,
    model_preset: str = 'monomer',
    use_small_bfd: bool = True,
    num_multimer_predictions_per_model: int = 5,
    is_run_relax: str = 'relax'
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
            'uniref30': config.UNIREF30_PATH,
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

    model_predict_relax = JobPredictRelaxOp(
        project=project,
        location=region,
        model_features=data_pipeline.outputs['features'],
        model_params=model_parameters.output,
        prediction_runners=run_config.outputs['model_runners'],
        run_multimer_system=run_config.outputs['run_multimer_system'],
        num_ensemble=run_config.outputs['num_ensemble'],
        is_run_relax=is_run_relax,
        tf_force_unified_memory=config.TF_FORCE_UNIFIED_MEMORY,
        xla_python_client_mem_fraction=config.XLA_PYTHON_CLIENT_MEM_FRACTION
    ).set_display_name('Predict/Relax')
