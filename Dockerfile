# Copyright 2022 Google LLC
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

FROM gcr.io/deeplearning-platform-release/base-cu110

ARG CUDA_MAJOR=11
ARG CUDA_MINOR=0
ARG ALPHAFOLD_VERSION=v2.2.0

SHELL ["/bin/bash", "-c"]

# Temporary fix to address NVIDIA key rotation till DLVM updates the keys in the base image
RUN apt-key del 7fa2af80 \
    && apt-key adv --fetch-keys https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2004/x86_64/3bf863cc.pub

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
      build-essential \
      cmake \
      cuda-command-line-tools-${CUDA_MAJOR}-${CUDA_MINOR} \
      git \
      hmmer \
      kalign \
      tzdata \
      wget \
    && rm -rf /var/lib/apt/lists/*

# Compile HHsuite from source.
RUN git clone --branch v3.3.0 https://github.com/soedinglab/hh-suite.git /tmp/hh-suite \
    && mkdir /tmp/hh-suite/build \
    && pushd /tmp/hh-suite/build \
    && cmake -DCMAKE_INSTALL_PREFIX=/opt/hhsuite .. \
    && make -j 4 && make install \
    && ln -s /opt/hhsuite/bin/* /usr/bin \
    && popd \
    && rm -rf /tmp/hh-suite

ENV PATH="/opt/conda/bin:$PATH"
RUN conda update -qy conda \
    && conda install -y -c conda-forge \
      openmm=7.5.1 \
      cudatoolkit==${CUDA_VERSION} \
      pdbfixer \
      pip \
      python=3.7

RUN git clone --branch $ALPHAFOLD_VERSION https://github.com/deepmind/alphafold.git /app/alphafold
RUN wget -q -P /app/alphafold/alphafold/common/ \
  https://git.scicore.unibas.ch/schwede/openstructure/-/raw/7102c63615b64735c4941278d92b554ec94415f8/modules/mol/alg/src/stereo_chemical_props.txt

# Install pip packages.
RUN pip3 install --upgrade pip \
    && pip3 install -r /app/alphafold/requirements.txt \
    && pip3 install py3Dmol tqdm \
    && pip3 install --upgrade jax==0.2.14 jaxlib==0.1.69+cuda${CUDA_MAJOR}${CUDA_MINOR} -f \
      https://storage.googleapis.com/jax-releases/jax_releases.html

# Apply OpenMM patch.
WORKDIR /opt/conda/lib/python3.7/site-packages
RUN patch -p0 < /app/alphafold/docker/openmm.patch

# Install Google vertex components
#RUN pip3 install -U google-cloud-aiplatform google-cloud-pipeline-components google-cloud-storage

WORKDIR /modules
ADD src/components/alphafold_utils.py .

ENV PYTHONPATH=/app/alphafold:/modules
RUN ldconfig
