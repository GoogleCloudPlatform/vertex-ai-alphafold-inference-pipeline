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


from re import I
from kfp.v2 import dsl
from kfp.v2.dsl import Artifact
from kfp.v2.dsl import Input
from kfp.v2.dsl import Output
from typing import List

from src import config


@dsl.component(
    base_image=config.ALPHAFOLD_COMPONENTS_IMAGE
)
def predict_relax(
    model_features: Input[Artifact],
    model_params: Input[Artifact],
    prediction_runners: list,
    num_ensemble: int,
    run_multimer_system: bool,
    is_run_relax: str,
    tf_force_unified_memory: str,
    xla_python_client_mem_fraction: str,
    raw_predictions: Output[Artifact],
    unrelaxed_proteins: Output[Artifact],
    relaxed_proteins: Output[Artifact],
):
    """Runs AlphaFold predictions and (optionally) relaxations sequentially."""

    import json
    import logging
    import os
    import time

    from alphafold_utils import predict_relax as alphafold_predict_relax

    os.makedirs(raw_predictions.path, exist_ok=True)
    os.makedirs(unrelaxed_proteins.path, exist_ok=True)
    os.makedirs(relaxed_proteins.path, exist_ok=True)

    os.environ['TF_FORCE_UNIFIED_MEMORY'] = tf_force_unified_memory
    os.environ['XLA_PYTHON_CLIENT_MEM_FRACTION'] = xla_python_client_mem_fraction

    logging.info(f'Starting predictions on {prediction_runners} ...')
    t0 = time.time()

    ranking_confidences = alphafold_predict_relax(
        model_features_path=model_features.path,
        model_params_path=model_params.path,
        prediction_runners=prediction_runners,
        num_ensemble=num_ensemble,
        run_multimer_system=run_multimer_system,
        run_relax=(is_run_relax == 'relax'),
        raw_prediction_path=raw_predictions.path,
        unrelaxed_protein_path=unrelaxed_proteins.path,
        relaxed_protein_path=relaxed_proteins.path,
    )

    raw_predictions.metadata['category'] = 'raw_predictions'
    raw_predictions.metadata['ranking_confidences'] = json.dumps(
        ranking_confidences)
    unrelaxed_proteins.metadata['category'] = 'unrelaxed_proteins'
    relaxed_proteins.metadata['category'] = 'relaxed_proteins'

    t1 = time.time()
    logging.info(f'Model predictions completed. Elapsed time: {t1-t0}')
