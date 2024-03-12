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
"""A component encapsulating AlphaFold model relaxation."""

from kfp.v2 import dsl
from kfp.v2.dsl import Artifact
from kfp.v2.dsl import Input
from kfp.v2.dsl import Output

import config as config
from typing import List


@dsl.component(
    base_image=config.ALPHAFOLD_COMPONENTS_IMAGE
)
def relax(
    unrelaxed_protein: Input[Artifact],
    relaxed_protein: Output[Artifact],
    max_iterations: int = 0,
    tolerance: float = 2.39,
    stiffness: float = 10.0,
    exclude_residues: List[str] = [],
    max_outer_iterations: int = 3,
    use_gpu: bool = True,
    tf_force_unified_memory: str = '',
    xla_python_client_mem_fraction: str = ''
):
  """Configures and runs Amber relaxation."""

  import logging
  import time
  import os

  from alphafold_utils import relax_protein

  os.environ['TF_FORCE_UNIFIED_MEMORY'] = tf_force_unified_memory
  os.environ['XLA_PYTHON_CLIENT_MEM_FRACTION'] = xla_python_client_mem_fraction

  t0 = time.time()
  logging.info('Starting model relaxation ...')

  relaxed_protein.uri = f'{relaxed_protein.uri}.pdb'
  relaxed_protein_pdb = relax_protein(
      unrelaxed_protein_path=unrelaxed_protein.path,
      relaxed_protein_path=relaxed_protein.path,
      max_iterations=max_iterations,
      tolerance=tolerance,
      stiffness=stiffness,
      exclude_residues=exclude_residues,
      max_outer_iterations=max_outer_iterations,
      use_gpu=use_gpu
  )

  relaxed_protein.metadata['category'] = 'relaxed_protein'

  t1 = time.time()
  logging.info(f'Model relaxation completed. Elapsed time: {t1-t0}')
