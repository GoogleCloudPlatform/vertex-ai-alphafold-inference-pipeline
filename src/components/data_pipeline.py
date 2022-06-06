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
"""A component encapsulating AlphaFold data pipelines."""

from kfp.v2 import dsl
from kfp.v2.dsl import Artifact
from kfp.v2.dsl import Input
from kfp.v2.dsl import Output
from src import config


@dsl.component(
    base_image=config.ALPHAFOLD_COMPONENTS_IMAGE
)
def data_pipeline(
    sequence: Input[Artifact],
    ref_databases: Input[Artifact],
    run_multimer_system: bool,
    use_small_bfd: bool,
    max_template_date: str,
    msas: Output[Artifact],
    features: Output[Artifact]
):
  """Configures and runs AlphaFold data pipelines."""

  import logging
  import os
  import time

  from alphafold_utils import run_data_pipeline

  logging.info(f'Starting {"multimer" if run_multimer_system else "monomer"} AlphaFold data pipeline')
  t0 = time.time()

  mount_path = ref_databases.uri
  uniref90_database_path = os.path.join(
      mount_path, ref_databases.metadata['uniref90'])
  mgnify_database_path = os.path.join(
      mount_path, ref_databases.metadata['mgnify'])
  uniclust30_database_path = os.path.join(
      mount_path, ref_databases.metadata['uniclust30'])
  bfd_database_path = os.path.join(
      mount_path, ref_databases.metadata['bfd'])
  small_bfd_database_path = os.path.join(
      mount_path, ref_databases.metadata['small_bfd'])
  uniprot_database_path = os.path.join(
      mount_path, ref_databases.metadata['uniprot'])
  pdb70_database_path = os.path.join(
      mount_path, ref_databases.metadata['pdb70'])
  obsolete_pdbs_path = os.path.join(
      mount_path, ref_databases.metadata['pdb_obsolete'])
  seqres_database_path = os.path.join(
      mount_path, ref_databases.metadata['pdb_seqres'])
  mmcif_path = os.path.join(mount_path, ref_databases.metadata['pdb_mmcif'])
  os.makedirs(msas.path, exist_ok=True)

  features_dict, msas_metadata = run_data_pipeline(
      fasta_path=sequence.path,
      run_multimer_system=run_multimer_system,
      use_small_bfd=use_small_bfd,
      uniref90_database_path=uniref90_database_path,
      mgnify_database_path=mgnify_database_path,
      bfd_database_path=bfd_database_path,
      small_bfd_database_path=small_bfd_database_path,
      uniclust30_database_path=uniclust30_database_path,
      uniprot_database_path=uniprot_database_path,
      pdb70_database_path=pdb70_database_path,
      obsolete_pdbs_path=obsolete_pdbs_path,
      seqres_database_path=seqres_database_path,
      mmcif_path=mmcif_path,
      max_template_date=max_template_date,
      msa_output_path=msas.path,
      features_output_path=features.path,
  )

  features.metadata['category'] = 'features'
  if run_multimer_system:
    features.metadata['final_dedup_msa_size'] = int(
        features_dict['num_alignments'])
  else:
    features.metadata['final_dedup_msa_size'] = int(
        features_dict['num_alignments'][0])
    features.metadata['total_number_templates'] = int(
        features_dict['template_domain_names'].shape[0])
  msas.metadata = msas_metadata

  t1 = time.time()
  logging.info(f'Data pipeline completed. Elapsed time: {t1-t0}')
