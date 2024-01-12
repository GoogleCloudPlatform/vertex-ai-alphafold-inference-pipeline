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
"""A component encapsulating AlphaFold hhblits tool."""

from typing import List
from kfp.v2 import dsl
from kfp.v2.dsl import Artifact
from kfp.v2.dsl import Input
from kfp.v2.dsl import Output

import sys
sys.path.append('..')
import config


@dsl.component(
    base_image=config.ALPHAFOLD_COMPONENTS_IMAGE
)
def hhblits(
    sequence: Input[Artifact],
    ref_databases: Input[Artifact],
    databases: List[str],
    msa: Output[Artifact],
    n_cpu: int = 12,
    maxseq: int = 1_000_000,
):
  """Configures and runs hhblits."""

  import logging
  import os
  import time

  from alphafold_utils import run_hhblits

  logging.info(f'Starting hhblits search on {databases}')
  t0 = time.time()

  mount_path = ref_databases.uri
  database_paths = [os.path.join(mount_path, ref_databases.metadata[database])
                    for database in databases]

  parsed_msa, msa_format = run_hhblits(
      input_path=sequence.path,
      database_paths=database_paths,
      msa_path=msa.path,
      n_cpu=n_cpu,
      maxseq=maxseq
  )

  msa.metadata['category'] = 'msa'
  msa.metadata['num_sequences'] = len(parsed_msa)
  msa.metadata['data_format'] = msa_format
  msa.metadata['databases'] = databases
  msa.metadata['tool'] = 'hhblits'

  t1 = time.time()
  logging.info(f'Hhblits search completed. Elapsed time: {t1-t0}')
