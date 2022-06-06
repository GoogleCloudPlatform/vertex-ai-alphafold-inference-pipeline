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
"""Script to start AlphaFold inference pipelines."""

import os

from absl import app
from absl import flags
import google.cloud.aiplatform as aip
from kfp.v2 import compiler


_PIPELINE_JOB_NAME_PREFIX = 'alphafold-inference'

FLAGS = flags.FLAGS

flags.DEFINE_string('pipeline_staging_location',
                    'gs://jk-mlops-bucket/pipelines',
                    'Vertex AI staging bucket')
flags.DEFINE_string('project', 'jk-mlops', 'GCP Project')
flags.DEFINE_string('region', 'us-central1', 'GCP Region')
flags.DEFINE_string('max_template_date', '2020-05-14', 'Max template date')
flags.DEFINE_string('vertex_sa',
                    'training-sa@jk-mlops-dev.iam.gserviceaccount.com',
                    'Vertex SA')
flags.DEFINE_string('pipelines_sa',
                    'pipelines-sa@jk-mlops-dev.iam.gserviceaccount.com',
                    'Pipelines SA')
flags.DEFINE_bool('compile_only', False, 'Compile only flag')
flags.DEFINE_string('nfs_server',
                    '10.71.1.10',
                    'IP address of an Filestore instance')
flags.DEFINE_string('nfs_path',
                    '/datasets_v1',
                    'Filestore file share with AlphaFold databases')
flags.DEFINE_string('network',
                    'projects/895222332033/global/networks/default',
                    'Filestore instance network')
flags.DEFINE_string('model_params_uri',
                    'gs://jk-mlops-bucket',
                    'GCS location of model params')
flags.DEFINE_enum('pipeline', 'original',
                  ['original', 'monomer_optimized', 'multimer_optimized'],
                  'Pipeline')
flags.DEFINE_enum('model_preset', 'monomer',
                  ['monomer', 'monomer_casp14', 'monomer_ptm', 'multimer'],
                  'Model preset')
flags.DEFINE_bool('enable_caching', False, 'Caching control')
flags.DEFINE_bool('use_small_bfd', False, 'Use small bfd')
flags.DEFINE_string('fasta_path',
                    'gs://jk-alphafold-datasets-archive/fasta/T1050.fasta',
                    'A path to a sequence')

def _main(argv):
  """Script to start AlphaFold inference pipelines."""
  os.environ['ALPHAFOLD_COMPONENTS_IMAGE'] = f'gcr.io/{FLAGS.project}/alphafold-components'
  os.environ['MODEL_PARAMS_GCS_LOCATION'] = FLAGS.model_params_uri
  os.environ['NFS_SERVER'] = FLAGS.nfs_server
  os.environ['NFS_PATH'] = FLAGS.nfs_path
  os.environ['NETWORK'] = FLAGS.network

  if FLAGS.pipeline == 'original':
    from src.pipelines.alphafold_inference_pipeline import (
        alphafold_inference_pipeline as pipeline)
  elif FLAGS.pipeline == 'monomer_optimized':
    from src.pipelines.alphafold_optimized_monomer import (
        alphafold_monomer_pipeline as pipeline)

  job_name = f'{_PIPELINE_JOB_NAME_PREFIX}_{FLAGS.pipeline}'
  compiler.Compiler().compile(
      pipeline_func=pipeline,
      package_path=f'{job_name}.json')

  if FLAGS.compile_only:
    return

  params = {
      'sequence_path': FLAGS.fasta_path,
      'project': FLAGS.project,
      'region': FLAGS.region,
      'max_template_date': FLAGS.max_template_date,
  }
  if FLAGS.pipeline == 'original':
    params['model_preset'] = FLAGS.model_preset
    if FLAGS.use_small_bfd:
      params['use_small_bfd'] = FLAGS.use_small_bfd

  pipeline_job = aip.PipelineJob(
      display_name=job_name,
      template_path=f'{job_name}.json',
      pipeline_root=f'{FLAGS.pipeline_staging_location}/{job_name}',
      parameter_values=params,
      enable_caching=FLAGS.enable_caching,
  )

  pipeline_job.run(service_account=FLAGS.pipelines_sa)


if __name__ == '__main__':
  app.run(_main)
