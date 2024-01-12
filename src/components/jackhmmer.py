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
"""A component encapsulating jackhmmer tool."""

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
def jackhmmer(
    sequence: Input[Artifact],
    ref_databases: Input[Artifact],
    database: str,
    msa: Output[Artifact],
    n_cpu: int = 8,
    maxseq: int = 10000,
):
  """Configures and runs jackhmmer."""

  import logging
  import os
  import time

  from alphafold_utils import run_jackhmmer

  logging.info(f'Starting jackhmmer search on {database}')
  t0 = time.time()

  mount_path = ref_databases.uri
  database_path = os.path.join(mount_path, ref_databases.metadata[database])

  parsed_msa, msa_format = run_jackhmmer(
      input_path=sequence.path,
      database_path=database_path,
      msa_path=msa.path,
      n_cpu=n_cpu,
      maxseq=maxseq
  )

  msa.metadata['category'] = 'msa'
  msa.metadata['num_sequences'] = len(parsed_msa)
  msa.metadata['data_format'] = 'sto'
  msa.metadata['databases'] = [database]
  msa.metadata['tool'] = 'jackhmmer'

  t1 = time.time()
  logging.info(f'Jackhmmer search completed. Elapsed time: {t1-t0}')
