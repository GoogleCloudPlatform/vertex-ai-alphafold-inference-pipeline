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

"""Submits a pipeline run."""

import gcsfs
import fsspec
import os

from absl import flags
from absl import app
from absl import logging
from datetime import datetime
from importlib import import_module

from google.cloud import aiplatform as vertex_ai



flags.DEFINE_string('project', 'jk-mlops-dev', 'GCP Project')
flags.DEFINE_string('region', 'us-central1', 'Vertex Pipelines region')
flags.DEFINE_string('staging_bucket', None, 'Staging bucket')
flags.DEFINE_string('pipelines_sa', 'pipelines-sa@jk-mlops-dev.iam.gserviceaccount.com', 'Pipelines SA')
flags.DEFINE_string('pipeline_template_path', None, 'A path to the output JSON file for the pipeline IR')
flags.DEFINE_string('params', None, 'Runtime parameters')
flags.DEFINE_string('experiment_id', None, 'Experiment ID')
flags.DEFINE_bool('enable_caching', True, 'Enable pipeline level caching')

flags.mark_flag_as_required('pipeline_template_path')
flags.mark_flag_as_required('params')

FLAGS = flags.FLAGS


def _maybe_bool(value: str):
    if value == 'True':
        value = True
    if value == 'False':
        value = False
    return value


def _convert_params(param_string: str) -> dict:
    params = {param.split('=')[0]: _maybe_bool(param.split('=')[1])
              for param in param_string.split(',')}
    return params


def _copy_sequence(local_path: str, gcs_path: str):
    local_fs = fsspec.filesystem('file')
    gcs_fs = gcsfs.GCSFileSystem()

    gcs_fs.put(local_path, gcs_path)



def _main(argv):
    params = _convert_params(FLAGS.params)

    if not os.path.exists(params['sequence_path']):
        raise FileNotFoundError('Invalid sequence path')

    if not os.path.exists(FLAGS.pipeline_template_path):
        raise FileNotFoundError('Invalid path to pipeline JSON')

    sequence_file_name = os.path.basename(params['sequence_path'])
    gcs_sequence_path = f'{FLAGS.staging_bucket}/fasta/{sequence_file_name}'

    logging.info(f'Copying {params["sequence_path"]} to {gcs_sequence_path}')
    _copy_sequence(params['sequence_path'], gcs_sequence_path)
    params['sequence_path'] = gcs_sequence_path

    vertex_ai.init(
        project=FLAGS.project,
        location=FLAGS.region,
        staging_bucket=FLAGS.staging_bucket,
    )

    pipeline_name = os.path.basename(FLAGS.pipeline_template_path).split('.')[0].lower()
    labels = {
        'experiment_id': FLAGS.experiment_id,
        'sequence_id': sequence_file_name.split('.')[0].lower()
    }

    pipeline_job = vertex_ai.PipelineJob(
        display_name=pipeline_name,
        template_path=FLAGS.pipeline_template_path,
        pipeline_root=f'{FLAGS.staging_bucket}/pipeline_runs/{pipeline_name}',
        parameter_values=params,
        enable_caching=FLAGS.enable_caching,
        labels=labels
    )

    pipeline_job.run(
        sync=False,
        service_account=FLAGS.pipelines_sa)

   




if __name__ == "__main__":
    app.run(_main)
