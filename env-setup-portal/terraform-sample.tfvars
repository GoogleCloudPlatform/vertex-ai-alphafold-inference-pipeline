# Copyright 2024 Google LLC
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

####################  INFRA VARIABLES  #################################

project_id              = "<PROJECT_ID>"
region                  = "<REGION>"
zone                    = "<ZONE>"
network_name            = "<NETWORK_NAME>"
subnet_name             = "<SUBNET_NAME>"
workbench_instance_name = "<WORKBENCH_INSTANCE_NAME>"
filestore_instance_id   = "<FILESTORE_INSTANCE_ID>"
gcs_bucket_name         = "<GCS_BUCKET_NAME>"
gcs_dbs_path            = "<GCS_DBS_PATH>"
ar_repo_name            = "<ARTIFACT_REGISTRY_REPO_NAME>"

####################  CLOUD RUN VARIABLES  #################################

oauth2_client_id        = "<CLIENT_ID>"
oauth2_client_secret    = "<CLIENT_SECRET>"
flask_secret            = "<FLASK_SECRET>"
is_gcr_io_repo          = "<IS_GCR_IO_REPO>"
