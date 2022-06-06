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
"""KFP component that creates an input sequence artifact and configure pipeline run settings."""

from typing import NamedTuple

from kfp.v2 import dsl
from kfp.v2.dsl import Artifact
from kfp.v2.dsl import Output
from src import config


@dsl.component(
    base_image=config.ALPHAFOLD_COMPONENTS_IMAGE
)
def configure_run(
    sequence_path: str,
    model_preset: str,
    sequence: Output[Artifact],
    random_seed: int = None,
    num_multimer_predictions_per_model: int = 5,
) -> NamedTuple(
    'ConfigureRunOutputs',
    [
        ('sequence_path', str),
        ('model_runners', list),
        ('run_multimer_system', bool),
        ('num_ensemble', int),
    ]
):
  """Configures a pipeline run."""

  import random
  import sys
  from collections import namedtuple
  from alphafold.data import parsers
  from alphafold.model import config
  from google.cloud import storage

  run_multimer_system = 'multimer' == model_preset
  num_ensemble = 8 if model_preset == 'monomer_casp14' else 1
  num_predictions_per_model = num_multimer_predictions_per_model if model_preset == 'multimer' else 1

  client = storage.Client()
  sequence.uri = f'{sequence.uri}.fasta'
  with open(sequence.path, 'wb') as f:
    client.download_blob_to_file(sequence_path, f)

  with open(sequence.path) as f:
    sequence_str = f.read()
  seqs, seq_descs = parsers.parse_fasta(sequence_str)

  if len(seqs) != 1 and model_preset != 'multimer':
    raise ValueError(
        f'More than one sequence found in {sequence_path}.',
        'Unsupported for monomer predictions.')

  models = config.MODEL_PRESETS[model_preset]
  if random_seed is None:
    random_seed = random.randrange(
        sys.maxsize // (len(models) * num_multimer_predictions_per_model)
    )

  model_runners = []
  for model_name in models:
    for i in range(num_predictions_per_model):
      model_runners.append({
          'prediction_index': i,
          'model_name': model_name,
          'random_seed': random_seed
      })
      random_seed += 1

  sequence.metadata['category'] = 'sequence'
  sequence.metadata['description'] = seq_descs
  sequence.metadata['num_residues'] = [len(seq) for seq in seqs]

  output = namedtuple('ConfigureRunOutputs',
                      ['sequence_path', 'model_runners',
                       'run_multimer_system', 'num_ensemble'])

  return output(sequence.path, model_runners, run_multimer_system, num_ensemble)
