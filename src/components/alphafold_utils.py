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

"""Utility functions that encapsulate AlphaFold inference components."""

import glob
import logging
import os
import pickle
import shutil
from typing import Dict, List, Mapping, Sequence, Tuple

from alphafold.common import protein
from alphafold.common import residue_constants
from alphafold.data import parsers
from alphafold.data import pipeline
from alphafold.data import pipeline_multimer
from alphafold.data import templates
from alphafold.data.pipeline import make_msa_features
from alphafold.data.pipeline import make_sequence_features
from alphafold.data.tools import hhblits
from alphafold.data.tools import hhsearch
from alphafold.data.tools import hmmsearch
from alphafold.data.tools import jackhmmer
from alphafold.model import config
from alphafold.model import data
from alphafold.model import model
from alphafold.relax import relax
import numpy as np


JACKHMMER_BINARY_PATH = shutil.which('jackhmmer')
HHBLITS_BINARY_PATH = shutil.which('hhblits')
HHSEARCH_BINARY_PATH = shutil.which('hhsearch')
HMMSEARCH_BINARY_PATH = shutil.which('hmmsearch')
KALIGN_BINARY_PATH = shutil.which('kalign')
HMMBUILD_BINARY_PATH = shutil.which('hmmbuild')

MAX_TEMPLATE_HITS = 20


def _load_features(features_path: str) -> Dict[str, str]:
  """Loads pickeled features."""
  with open(features_path, 'rb') as f:
    features = pickle.load(f)
  return features


def _read_msa(msa_path: str, msa_format: str) -> str:
  """Reads and parses an MSA file."""
  if os.path.exists(msa_path):
    with open(msa_path) as f:
      msa = f.read()
    if msa_format == 'sto':
      msa = parsers.parse_stockholm(msa)
    elif msa_format == 'a3m':
      msa = parsers.parse_a3m(msa)
    else:
      raise RuntimeError(f'Unsupported MSA format: {msa_format}')
  return msa


def _read_sequence(sequence_path: str) -> Tuple[str, str, int]:
  """Reads and parses a FASTA sequence file."""
  with open(sequence_path) as f:
    sequence_str = f.read()
  sequences, sequence_descs = parsers.parse_fasta(sequence_str)
  if len(sequences) != 1:
    raise ValueError(f'More than one input sequence found in {sequence_path}.')
  return sequences[0], sequence_descs[0], len(sequences[0])


def _read_template_features(template_features_path) -> Dict[str, str]:
  """Reads and unpickles a pdb structure."""
  with open(template_features_path, 'rb') as f:
    template_features = pickle.load(f)
  return template_features


def run_data_pipeline(
    fasta_path: str,
    run_multimer_system: bool,
    uniref90_database_path: str,
    mgnify_database_path: str,
    bfd_database_path: str,
    small_bfd_database_path: str,
    uniclust30_database_path: str,
    uniprot_database_path: str,
    pdb70_database_path: str,
    obsolete_pdbs_path: str,
    seqres_database_path: str,
    mmcif_path: str,
    max_template_date: str,
    msa_output_path: str,
    features_output_path: str,
    use_small_bfd: bool,
) -> Dict[str, str]:
  """Runs AlphaFold data pipeline."""
  if run_multimer_system:
    template_searcher = hmmsearch.Hmmsearch(
        binary_path=HMMSEARCH_BINARY_PATH,
        hmmbuild_binary_path=HMMBUILD_BINARY_PATH,
        database_path=seqres_database_path)
    template_featurizer = templates.HmmsearchHitFeaturizer(
        mmcif_dir=mmcif_path,
        max_template_date=max_template_date,
        max_hits=MAX_TEMPLATE_HITS,
        kalign_binary_path=KALIGN_BINARY_PATH,
        release_dates_path=None,
        obsolete_pdbs_path=obsolete_pdbs_path)
  else:
    template_searcher = hhsearch.HHSearch(
        binary_path=HHSEARCH_BINARY_PATH,
        databases=[pdb70_database_path])
    template_featurizer = templates.HhsearchHitFeaturizer(
        mmcif_dir=mmcif_path,
        max_template_date=max_template_date,
        max_hits=MAX_TEMPLATE_HITS,
        kalign_binary_path=KALIGN_BINARY_PATH,
        release_dates_path=None,
        obsolete_pdbs_path=obsolete_pdbs_path)

  monomer_data_pipeline = pipeline.DataPipeline(
      jackhmmer_binary_path=JACKHMMER_BINARY_PATH,
      hhblits_binary_path=HHBLITS_BINARY_PATH,
      uniref90_database_path=uniref90_database_path,
      mgnify_database_path=mgnify_database_path,
      bfd_database_path=bfd_database_path,
      uniclust30_database_path=uniclust30_database_path,
      small_bfd_database_path=small_bfd_database_path,
      template_searcher=template_searcher,
      template_featurizer=template_featurizer,
      use_small_bfd=use_small_bfd)

  if run_multimer_system:
    data_pipeline = pipeline_multimer.DataPipeline(
        monomer_data_pipeline=monomer_data_pipeline,
        jackhmmer_binary_path=JACKHMMER_BINARY_PATH,
        uniprot_database_path=uniprot_database_path)
  else:
    data_pipeline = monomer_data_pipeline

  feature_dict = data_pipeline.process(
      input_fasta_path=fasta_path,
      msa_output_dir=msa_output_path
  )

  with open(features_output_path, 'wb') as f:
    pickle.dump(feature_dict, f, protocol=4)

  msas_metadata = {}
  paths = glob.glob(os.path.join(msa_output_path, '**'), recursive=True)
  paths = [path for path in paths if os.path.isfile(path)]

  if run_multimer_system:
    folders = [os.path.join(msa_output_path, folder)
               for folder in  os.listdir(msa_output_path)
               if os.path.isdir(os.path.join(msa_output_path, folder))]
    paths = []
    for folder in folders:
      paths += [os.path.join(folder, file) for file in  os.listdir(folder)]
  else:
    paths = [os.path.join(msa_output_path, file)
             for file in os.listdir(msa_output_path)]
  for file in paths:
    with open(file, 'r') as f:
      artifact = f.read()
    file_format = file.split('.')[-1]
    if file_format == 'sto':
      artifact = parsers.parse_stockholm(artifact)
    elif file_format == 'a3m':
      artifact = parsers.parse_a3m(artifact)
    elif file_format == 'hhr':
      artifact = parsers.parse_hhr(artifact)
    else:
      raise ValueError('Unknown artifact type')
    msas_metadata[os.path.join(
        file.split(os.sep)[-2], file.split(os.sep)[-1])] = len(artifact)

  return feature_dict, msas_metadata


def predict(
    model_features_path: str,
    model_params_path: str,
    model_name: str,
    num_ensemble: int,
    run_multimer_system: bool,
    random_seed: int,
    raw_prediction_path: str,
    unrelaxed_protein_path: str,
) -> Mapping[str, str]:
  """Runs inference on an AlphaFold model."""

  model_config = config.model_config(model_name)
  if run_multimer_system:
    model_config.model.num_ensemble_eval = num_ensemble
  else:
    model_config.data.eval.num_ensemble_eval = num_ensemble

  model_params = data.get_model_haiku_params(
      model_name=model_name, data_dir=model_params_path)
  model_runner = model.RunModel(model_config, model_params)

  features = _load_features(model_features_path)
  processed_feature_dict = model_runner.process_features(
      raw_features=features,
      random_seed=random_seed)

  prediction_result = model_runner.predict(
      feat=processed_feature_dict,
      random_seed=random_seed)

  with open(raw_prediction_path, 'wb') as f:
    pickle.dump(prediction_result, f, protocol=4)

  plddt = prediction_result['plddt']
  plddt_b_factors = np.repeat(
      plddt[:, None], residue_constants.atom_type_num, axis=-1)
  unrelaxed_structure = protein.from_prediction(
      features=processed_feature_dict,
      result=prediction_result,
      b_factors=plddt_b_factors,
      remove_leading_feature_dimension=not model_runner.multimer_mode)
  unrelaxed_pdbs = protein.to_pdb(unrelaxed_structure)
  with open(unrelaxed_protein_path, 'w') as f:
    f.write(unrelaxed_pdbs)

  return prediction_result


def relax_protein(
    unrelaxed_protein_path: str,
    relaxed_protein_path: str,
    max_iterations: int = 0,
    tolerance: float = 2.39,
    stiffness: float = 10.0,
    exclude_residues: list[str] = [],
    max_outer_iterations: int = 3,
    use_gpu=False
) -> Mapping[str, str]:
  """Runs AMBER relaxation."""

  with open(unrelaxed_protein_path, 'r') as f:
    unrelaxed_protein_pdb = f.read()

  unrelaxed_structure = protein.from_pdb_string(unrelaxed_protein_pdb)
  amber_relaxer = relax.AmberRelaxation(
      max_iterations=max_iterations,
      tolerance=tolerance,
      stiffness=stiffness,
      exclude_residues=exclude_residues,
      max_outer_iterations=max_outer_iterations,
      use_gpu=use_gpu)
  relaxed_protein_pdb, _, _ = amber_relaxer.process(prot=unrelaxed_structure)

  logging.info(f'Saving relaxed protein to {relaxed_protein_path}')
  with open(relaxed_protein_path, 'w') as f:
    f.write(relaxed_protein_pdb)

  return relaxed_protein_pdb


def aggregate(
    sequence_path: str,
    msa_paths: List[Tuple[str, str]],
    template_features_path: str,
    output_features_path: str
) -> Dict[str, str]:
  """Aggregates MSAs and template features to create model features."""

  # Create sequence features
  seq, seq_desc, num_res = _read_sequence(sequence_path)
  sequence_features = make_sequence_features(
      sequence=seq,
      description=seq_desc,
      num_res=num_res
  )
  # Create MSA features
  msas = []
  for msa_path, msa_format in msa_paths:
    msas.append(_read_msa(msa_path, msa_format))
  if not msas:
    raise RuntimeError('No MSAs passed to the component')
  msa_features = make_msa_features(msas=msas)
  # Create template features
  template_features = _read_template_features(template_features_path)

  model_features = {
      **sequence_features,
      **msa_features,
      **template_features
  }
  with open(output_features_path, 'wb') as f:
    pickle.dump(model_features, f, protocol=4)

  return model_features


def run_jackhmmer(
    input_path: str,
    msa_path: str,
    database_path: str,
    maxseq: int,
    n_cpu: int = 8
):
  """Runs jackhmeer and saves results to files."""

  runner = jackhmmer.Jackhmmer(
      binary_path=JACKHMMER_BINARY_PATH,
      database_path=database_path,
      n_cpu=n_cpu,
  )

  results = runner.query(input_path, maxseq)[0]
  with open(msa_path, 'w') as f:
    f.write(results['sto'])

  return parsers.parse_stockholm(results['sto']), 'sto'


def run_hhblits(
    input_path: str,
    msa_path: str,
    database_paths: Sequence[str],
    n_cpu: int,
    maxseq: int
):
  """Runs hhblits and saves results to a file."""

  runner = hhblits.HHBlits(
      binary_path=HHBLITS_BINARY_PATH,
      databases=database_paths,
      n_cpu=n_cpu,
      maxseq=maxseq,
  )

  results = runner.query(input_path)[0]
  with open(msa_path, 'w') as f:
    f.write(results['a3m'])

  return parsers.parse_a3m(results['a3m']), 'a3m'


def run_hhsearch(
    sequence_path: str,
    msa_path: str,
    msa_data_format: str,
    template_hits_path: str,
    template_features_path: str,
    template_dbs_paths: list[str],
    mmcif_path: str,
    obsolete_path: str,
    max_template_date: str,
    max_template_hits: int,
    maxseq: int
):
  """Runs hhsearch and saves results to a file."""

  if msa_data_format != 'sto' and msa_data_format != 'a3m':
    raise ValueError(f'Unsupported MSA format: {msa_data_format}')

  sequence, _, _ = _read_sequence(sequence_path)

  template_searcher = hhsearch.HHSearch(
      binary_path=HHSEARCH_BINARY_PATH,
      databases=template_dbs_paths,
      maxseq=maxseq
  )

  template_featurizer = templates.HhsearchHitFeaturizer(
      mmcif_dir=mmcif_path,
      max_template_date=max_template_date,
      max_hits=max_template_hits,
      kalign_binary_path=KALIGN_BINARY_PATH,
      obsolete_pdbs_path=obsolete_path,
      release_dates_path=None,
  )

  with open(msa_path) as f:
    msa_str = f.read()

  if  msa_data_format == 'sto':
    msa_for_templates = parsers.deduplicate_stockholm_msa(msa_str)
    msa_for_templates = parsers.remove_empty_columns_from_stockholm_msa(
        msa_for_templates)
    msa_for_templates = parsers.convert_stockholm_to_a3m(msa_for_templates)

  hhr_str = template_searcher.query(msa_for_templates)
  with open(template_hits_path, 'w') as f:
    f.write(hhr_str)

  template_hits = template_searcher.get_template_hits(
      output_string=hhr_str, input_sequence=sequence)
  templates_result = template_featurizer.get_templates(
      query_sequence=sequence,
      hits=template_hits)
  with open(template_features_path, 'wb') as f:
    pickle.dump(templates_result.features, f, protocol=4)

  return parsers.parse_hhr(hhr_str), templates_result.features


def run_hmmsearch(
    sequence_path: str,
    msa_path: str,
    msa_data_format: str,
    template_hits_path: str,
    template_features_path: str,
    template_db_path: str,
    mmcif_path: str,
    obsolete_path: str,
    max_template_date,
    max_template_hits
):
  """Runs hhsearch and saves results to a file."""

  if msa_data_format != 'sto':
    raise ValueError(f'Unsupported MSA format: {msa_data_format}')

  sequence, _, _ = _read_sequence(sequence_path)

  template_searcher = hmmsearch.Hmmsearch(
      binary_path=HMMSEARCH_BINARY_PATH,
      hmmbuild_binary_path=HMMBUILD_BINARY_PATH,
      database_path=template_db_path
  )

  template_featurizer = templates.HmmsearchHitFeaturizer(
      mmcif_dir=mmcif_path,
      max_template_date=max_template_date,
      max_hits=max_template_hits,
      kalign_binary_path=KALIGN_BINARY_PATH,
      obsolete_pdbs_path=obsolete_path,
      release_dates_path=None
  )

  with open(msa_path) as f:
    msa_str = f.read()

  msa_for_templates = parsers.deduplicate_stockholm_msa(msa_str)
  msa_for_templates = parsers.remove_empty_columns_from_stockholm_msa(
      msa_for_templates)

  sto_str = template_searcher.query(msa_for_templates)
  with open(template_hits_path, 'w') as f:
    f.write(sto_str)

  template_hits = template_searcher.get_template_hits(
      output_string=sto_str, input_sequence=sequence)
  templates_result = template_featurizer.get_templates(
      query_sequence=sequence,
      hits=template_hits)

  with open(template_features_path, 'wb') as f:
    pickle.dump(templates_result.features, f, protocol=4)

  return parsers.parse_stockholm(template_hits), templates_result.features
