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



resource "null_resource" "copy_datasets" {
  provisioner "local-exec" {
    command = <<EOT
_REGION=${var.region}
_PROJECT_ID=${data.google_project.project.project_id}
_PROJECT_NUMBER=${data.google_project.project.number}
_NETWORK_ID=${google_compute_network.network.id}
_NETWORK_ID=$(echo $_NETWORK_ID | sed "s#$_PROJECT_ID#$_PROJECT_NUMBER#")
_FILESTORE_IP=${google_filestore_instance.filestore_instance.networks.0.ip_addresses.0}
_FILESHARE=${google_filestore_instance.filestore_instance.file_shares.0.name}
_GCS_PATH=gs://${var.gcs_dbs_path}
_GCS_PARAMS_PATH=gs://${google_storage_bucket.artifact_repo.name}
_MOUNT_POINT=/mnt/nfs/alphafold

gsutil -m cp -r $_GCS_PATH/params/ $_GCS_PARAMS_PATH

sed -i s#NETWORK_ID#$_NETWORK_ID#g vertex-training-template.yaml 
sed -i s#FILESTORE_IP#$_FILESTORE_IP#g vertex-training-template.yaml
sed -i s#FILESHARE#$_FILESHARE#g vertex-training-template.yaml
sed -i s#MOUNT_POINT#$_MOUNT_POINT#g vertex-training-template.yaml
sed -i s#GCS_PATH#$_GCS_PATH#g vertex-training-template.yaml

gcloud ai custom-jobs create --region $_REGION --display-name populate_filestore --config vertex-training-template.yaml
EOT
  }
  triggers = {
    always_run = timestamp()
  }
}
