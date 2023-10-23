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


variable "oauth2_client_id" {
  description = "The GCP project ID"
  type        = string
}

variable "oauth2_client_secret" {
  description = "The GCP project ID"
  type        = string
}

variable "flask_secret" {
  description = "The GCP project ID"
  type        = string
}

variable "project_id" {
  description = "The GCP project ID"
  type        = string
}

variable "region" {
  description = "The GCP project ID"
  type        = string
}

variable "zone" {
  description = "The GCP project ID"
  type        = string
}

variable "cloud_run_service_name" {
  description = "The GCP project ID"
  type        = string
  default     = "alphafoldportal"
}

variable "ar_repo_name" {
  description = "The GCP project ID"
  type        = string
}

variable "filestore_instance_id" {
  description = "The GCP project ID"
  type        = string
}

variable "bucket_name" {
  description = "The GCP project ID"
  type        = string
}

variable "machine_type" {
  description = "The pipeline instance's machine type"
  type        = string
  default     = "g2-standard-64"
}

