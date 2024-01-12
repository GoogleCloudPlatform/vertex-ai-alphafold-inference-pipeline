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

"""A utility to check if the FASTA file is valid."""

from Bio import SeqIO
from typing import Dict, Union

def validate_fasta_file(
    file_path: str
) -> Union[bool, Dict[int, int]]:
    """Parse and validate fasta file."""
    is_monomer = None
    sequences = {}

    with open(file_path, "r") as handle:
        fasta = SeqIO.parse(handle, "fasta")
        for i, s in enumerate(fasta):
            sequences[i] = len(s.seq)

    if not sequences:
        raise FileNotFoundError(
            'No sequences found in the FASTA file. ' +
            'Please provide a valid FASTA file.'
        )
    elif 0 in sequences.values():
        raise FileNotFoundError(
            'One or more sequences with 0 residues. ' +
            'Please check your FASTA file for inconsistencies.'
        )
    else:
        is_monomer = True if len(sequences) == 1 else False

    return is_monomer, sequences
