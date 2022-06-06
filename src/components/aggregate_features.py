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
"""A KFP component encapsulating AlphaFold feature aggregation logic."""

from kfp.v2 import dsl
from kfp.v2.dsl import Artifact
from kfp.v2.dsl import Input
from kfp.v2.dsl import Output

from src import config


@dsl.component(
    base_image=config.ALPHAFOLD_COMPONENTS_IMAGE
)
def aggregate_features(
    sequence: Input[Artifact],
    msa1: Input[Artifact],
    msa2: Input[Artifact],
    msa3: Input[Artifact],
    msa4: Input[Artifact],
    template_features: Input[Artifact],
    features: Output[Artifact],
):
  """Aggregates MSAs and template features to create model features."""
  import logging
  import time
  from alphafold_utils import aggregate

  logging.info('Starting feature aggregation ...')
  t0 = time.time()
  msa_paths = []
  msa_paths.append((msa1.path, msa1.metadata['data_format']))
  msa_paths.append((msa2.path, msa2.metadata['data_format']))
  msa_paths.append((msa3.path, msa3.metadata['data_format']))
  msa_paths.append((msa4.path, msa4.metadata['data_format']))
  model_features = aggregate(
      sequence_path=sequence.path,
      msa_paths=msa_paths,
      template_features_path=template_features.path,
      output_features_path=features.path
  )
  features.metadata['category'] = 'features'
  features.metadata['data_format'] = 'pkl'
  features.metadata['final_dedup_msa_size'] = int(
      model_features['num_alignments'][0]
  )
  features.metadata['total_num_templates'] = int(
      model_features['template_domain_names'].shape[0]
  )
  t1 = time.time()
  logging.info(f'Feature aggregation completed. Elapsed time: {t1-t0}')
