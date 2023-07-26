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

  triggers = {
    always_run = timestamp()
    REGION=var.region
    PROJECT_ID=data.google_project.project.project_id
    PROJECT_NUMBER=data.google_project.project.number
    NETWORK_ID=google_compute_network.network.id
    FILESTORE_IP=google_filestore_instance.filestore_instance.networks.0.ip_addresses.0
    FILESHARE=google_filestore_instance.filestore_instance.file_shares.0.name
  }
  
  provisioner "local-exec" {
    command = <<EOT
                NETWORK_ID=$(echo ${self.triggers.NETWORK_ID} | sed "s#${self.triggers.PROJECT_ID}#${self.triggers.PROJECT_NUMBER}#")
                GCS_PATH=gs://${var.gcs_dbs_path}
                GCS_PARAMS_PATH=gs://${google_storage_bucket.artifact_repo.name}
                MOUNT_POINT=/mnt/nfs/alphafold

                gsutil -m cp -r $GCS_PATH/params/ $GCS_PARAMS_PATH

                sed -i s#NETWORK_ID#$NETWORK_ID#g vertex-training-template.yaml 
                sed -i s#FILESTORE_IP#${self.triggers.FILESTORE_IP}#g vertex-training-template.yaml
                sed -i s#FILESHARE#${self.triggers.FILESHARE}#g vertex-training-template.yaml
                sed -i s#MOUNT_POINT#$MOUNT_POINT#g vertex-training-template.yaml
                sed -i s#GCS_PATH#$GCS_PATH#g vertex-training-template.yaml

                gcloud ai custom-jobs create --region ${self.triggers.REGION} --display-name populate_filestore --config vertex-training-template.yaml
                EOT
  }

  provisioner "local-exec" {
    when    = destroy
    command = <<EOT
                gcloud ai custom-jobs list --project alphafold-dev-392019 --region us-central1 --filter="displayName: populate_filestore AND state: JOB_STATE_PENDING"
                gcloud ai custom-jobs cancel populate_filestore --region ${self.triggers.REGION}
                EOT
    on_failure = continue
  }

}
