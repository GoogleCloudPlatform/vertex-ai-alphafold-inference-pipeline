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
"""A component encapsulating AlphaFold model predict."""


from kfp.v2 import dsl
from kfp.v2.dsl import Artifact
from kfp.v2.dsl import Input
from kfp.v2.dsl import Output

from src import config


@dsl.component(
    base_image=config.ALPHAFOLD_COMPONENTS_IMAGE
)
def predict(
    model_features: Input[Artifact],
    model_params: Input[Artifact],
    model_name: str,
    prediction_index: int,
    num_ensemble: int,
    run_multimer_system: bool,
    random_seed: int,
    raw_prediction: Output[Artifact],
    unrelaxed_protein: Output[Artifact]
):
  """Configures and runs AlphaFold model runner."""

  import logging
  import time

  from alphafold_utils import predict as alphafold_predict

  logging.info(f'Starting model prediction {prediction_index} using model {model_name}...')
  t0 = time.time()

  raw_prediction.uri = f'{raw_prediction.uri}.pkl'
  unrelaxed_protein.uri = f'{unrelaxed_protein.uri}.pdb'
  prediction_result = alphafold_predict(
      model_features_path=model_features.path,
      model_params_path=model_params.path,
      model_name=model_name,
      num_ensemble=num_ensemble,
      run_multimer_system=run_multimer_system,
      random_seed=random_seed,
      raw_prediction_path=raw_prediction.path,
      unrelaxed_protein_path=unrelaxed_protein.path
  )

  raw_prediction.metadata['category'] = 'raw_prediction'
  raw_prediction.metadata['prediction_index'] = prediction_index
  raw_prediction.metadata['ranking_confidence'] = prediction_result[
      'ranking_confidence']
  unrelaxed_protein.metadata['category'] = 'unrelaxed_protein'

  t1 = time.time()
  logging.info(f'Model prediction completed. Elapsed time: {t1-t0}')
