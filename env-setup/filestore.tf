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

resource "google_filestore_instance" "filestore_instance" {
  provider = google-beta
  name     = var.filestore_instance_id
  location = var.zone
  tier     = var.filestore_tier

  file_shares {
    capacity_gb = var.share_capacity
    name        = var.filesharename
  }

  networks {
    network      = google_compute_network.network.id
    modes        = ["MODE_IPV4"]
    connect_mode = "PRIVATE_SERVICE_ACCESS"
  }

  labels = {
    goog-packaged-solution = "target-and-lead-id"
  }

  depends_on = [
    google_service_networking_connection.service_connection
  ]

}
