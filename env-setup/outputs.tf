
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


output "filestore_ip" {
    value = google_filestore_instance.filestore_instance.networks.0.ip_addresses.0
}

output "network_id" {
    value = google_compute_network.network.id
}

output "fileshare" {
    value = google_filestore_instance.filestore_instance.file_shares.0.name
}

output "project_id" {
    value = data.google_project.project.project_id
}

output "project_number" {
    value = data.google_project.project.number
}

output "bucket_name" {
    value = google_storage_bucket.artifact_repo.name
}

