# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Config definitions for pipeline execution."""

import os


NFS_SERVER = os.getenv('NFS_SERVER')
NFS_PATH = os.getenv('NFS_PATH')
NFS_MOUNT_POINT = os.getenv('NFS_MOUNT_POINT', '/mnt/nfs/alphafold')
NETWORK = os.getenv('NETWORK')

MODEL_PARAMS_GCS_LOCATION = os.getenv('MODEL_PARAMS_GCS_LOCATION')

UNIREF90_PATH = os.getenv('UNIREF90_PATH', 'uniref90/uniref90.fasta')
MGNIFY_PATH = os.getenv('MGNIFY_PATH', 'mgnify/mgy_clusters_2018_12.fa')
BFD_PATH = os.getenv(
    'BFD_PATH',
    'bfd/bfd_metaclust_clu_complete_id30_c90_final_seq.sorted_opt')
SMALL_BFD_PATH = os.getenv('SMALL_BFD_PATH',
                           'small_bfd/bfd-first_non_consensus_sequences.fasta')
UNICLUST30_PATH = os.getenv('UNICLUST30_PATH',
                            'uniclust30/uniclust30_2018_08/uniclust30_2018_08')
UNIPROT_PATH = os.getenv('UNIPROT_PATH', 'uniprot/uniprot.fasta')
PDB70_PATH = os.getenv('PDB70_PATH', 'pdb70/pdb70')
PDB_MMCIF_PATH = os.getenv('PDB_MMCIF_PATH', 'pdb_mmcif/mmcif_files')
PDB_OBSOLETE_PATH = os.getenv('PDB_OBSOLETE_PATH', 'pdb_mmcif/obsolete.dat')
PDB_SEQRES_PATH = os.getenv('PDB_SEQRES_PATH', 'pdb_seqres/pdb_seqres.txt')

UNIREF_MAX_HITS = int(os.getenv('UNIREF_MAX_HITS', '10000'))
MGNIFY_MAX_HITS = int(os.getenv('MGNIFY_MAX_HITS', '501'))

DATA_PIPELINE_MACHINE_TYPE = os.getenv(
    'DATA_PIPELINE_MACHINE_TYPE', 'c2-standard-16')
JACKHMMER_MACHINE_TYPE = os.getenv('JACKHMMER_MACHINE_TYPE', 'n1-standard-8')
HHSEARCH_MACHINE_TYPE = os.getenv('HHSEARCH_MACHINE_TYPE', 'c2-standard-16')
HMMSEARCH_MACHINE_TYPE = os.getenv('HMMSEARCH_MACHINE_TYPE', 'c2-standard-16')
HHBLITS_MACHINE_TYPE = os.getenv('HMMSEARCH_MACHINE_TYPE', 'c2-standard-16')

MEMORY_LIMIT = os.getenv('MEMORY_LIMIT', '32')
CPU_LIMIT = os.getenv('CPU_LIMIT', '8')
GPU_LIMIT = os.getenv('GPU_LIMIT', '1')
GPU_TYPE = os.getenv('GPU_TYPE', 'nvidia-tesla-t4')
GKE_ACCELERATOR_KEY = 'cloud.google.com/gke-accelerator'

RELAX_MEMORY_LIMIT = os.getenv('RELAX_MEMORY_LIMIT', '32')
RELAX_CPU_LIMIT = os.getenv('RELAX_CPU_LIMIT', '8')
RELAX_GPU_LIMIT = os.getenv('RELAX_GPU_LIMIT', '1')
RELAX_GPU_TYPE = os.getenv('RELAX_GPU_TYPE', 'nvidia-tesla-t4')

ALPHAFOLD_COMPONENTS_IMAGE = os.getenv('ALPHAFOLD_COMPONENTS_IMAGE')

PARALLELISM = int(os.getenv('PARALLELISM', 5))

XLA_PYTHON_CLIENT_MEM_FRACTION = os.getenv(
    'XLA_PYTHON_CLIENT_MEM_FRACTION', '4.0')
TF_FORCE_UNIFIED_MEMORY = os.getenv('TF_FORCE_UNIFIED_MEMORY', '1')

