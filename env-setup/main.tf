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

terraform {
  required_version = ">= 0.14"
  required_providers {
    google = "~> 4.15"
  }
  #    backend "gcs" {
  #    bucket  = "PROJECT_ID-tf-state"
  #    prefix  = "af-demo"
  #  }
}

provider "google" {
  project = var.project_id
}

provider "google-beta" {
  project = var.project_id
}

data "google_project" "project" {
  project_id = var.project_id
}

# Enable required APIs
resource "google_project_service" "enable_required_services" {
  project            = var.project_id
  disable_on_destroy = false
  for_each           = toset([
    "artifactregistry.googleapis.com",
    "cloudbuild.googleapis.com",
    "compute.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "iamcredentials.googleapis.com",
    "iam.googleapis.com",
    "container.googleapis.com",
    "cloudtrace.googleapis.com",
    "monitoring.googleapis.com",
    "logging.googleapis.com",
    "notebooks.googleapis.com",
    "aiplatform.googleapis.com",
    "file.googleapis.com",
    "servicenetworking.googleapis.com",
    "storage.googleapis.com",
    "run.googleapis.com"
  ])
  service = each.key
}

