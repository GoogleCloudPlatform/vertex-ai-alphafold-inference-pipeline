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

"""Utils for minimization."""
import io
from . import residue_constants
from Bio import PDB
import numpy as np


def overwrite_b_factors(pdb_str: str, bfactors: np.ndarray) -> str:
  """Overwrites the B-factors in pdb_str with contents of bfactors array.
  Args:
    pdb_str: An input PDB string.
    bfactors: A numpy array with shape [1, n_residues, 37]. We assume that the
      B-factors are per residue; i.e. that the nonzero entries are identical in
      [0, i, :].
  Returns:
    A new PDB string with the B-factors replaced.
  """
  if bfactors.shape[-1] != residue_constants.atom_type_num:
    raise ValueError(
        f'Invalid final dimension size for bfactors: {bfactors.shape[-1]}.')

  parser = PDB.PDBParser(QUIET=True)
  handle = io.StringIO(pdb_str)
  structure = parser.get_structure('', handle)

  curr_resid = ('', '', '')
  idx = -1
  for atom in structure.get_atoms():
    atom_resid = atom.parent.get_id()
    if atom_resid != curr_resid:
      idx += 1
      if idx >= bfactors.shape[0]:
        raise ValueError('Index into bfactors exceeds number of residues. '
                         'B-factors shape: {shape}, idx: {idx}.')
    curr_resid = atom_resid
    atom.bfactor = bfactors[idx, residue_constants.atom_order['CA']]
  
  new_pdb = 'to_visualize.pdb'
  pdb_io = PDB.PDBIO()
  pdb_io.set_structure(structure)
  pdb_io.save(new_pdb)

  with open('to_visualize.pdb') as fp:
    to_visualize_pdb = fp.read()
  
  return to_visualize_pdb
