
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


variable "project_id" {
    description = "The GCP project ID"
    type        = string
}

variable "region" {
    description = "The region for the environment resources"
    type        = string
}

variable "zone" {
    description = "The zone for a Vertex Notebook instance"
    type        = string
}

variable "network_name" {
    description = "The network name"
    type        = string
}

variable "subnet_name" {
    description = "The subnet name"
    type        = string
}

variable "workbench_instance_name" {
    description = "The name of the Workbench instance"
    type        = string
}

variable "filestore_instance_id" {
    description = "he instance ID of the Filestore instance"
    type        = string
}

variable "gcs_bucket_name" {
    description = "The GCS bucket name"
    type        = string
}

variable "machine_type" {
    description = "The Notebook instance's machine type"
    type        = string
    default     = "n1-standard-8"
}


variable "boot_disk_size" {
    description = "The size of the boot disk"
    default     = 200
}

variable "share_capacity" {
    description = "Filstore share capacity"
    default = 3072
}

variable "filestore_tier" {
    description = "Filstore instance type"
    default = "BASIC_SSD"
}

variable "filesharename" {
    description = "The name of a fileshare"
    default = "datasets"
}

variable "image_family" {
    description = "A Deep Learning image family for the Notebook instance"
    type        = string
    default     = "common-cpu-notebooks"
}

variable "force_destroy" {
    description = "Whether to remove the bucket on destroy"
    type        = bool
    default     = false
}

variable "training_sa_roles" {
  description = "The roles to assign to the Vertex Training service account"
  default = [
    "storage.admin",
    "aiplatform.user"
    ] 
}

variable "pipelines_sa_roles" {
  description = "The roles to assign to the Vertex Pipelines service account"
  default = [    
    "storage.admin", 
    "aiplatform.user"
  ]
}


variable "training_sa_name" {
    description = "Vertex training service account name."
    default = "training-sa"
}

variable "pipelines_sa_name" {
    description = "Vertex pipelines service account name."
    default = "pipelines-sa"
}

variable "compute_engine_sa_roles" {
  description = "The roles to assign to the Default Compute Engine service acount"
  default = [    
    "storage.objectAdmin", 
    "aiplatform.user"
  ]
}

variable "cloud_build_sa_roles" {
  description = "The roles to assign to the Cloud Build service acount"
  default = [    
    "storage.objectAdmin", 
    "editor"
  ]
}

variable "subnet_ip_range" {
  description = "The IP address range for the subnet"
  default     = "10.129.0.0/20"
}

variable "peering_ip_range" {
  description = "The IP address range for service network peering"
  default     = "10.130.0.0/16"
}

variable "gcs_dbs_path" {
    description = "A GCS location of AlphaFold reference datasets"
    type        = string
}

variable "uniform_bucket_access" {
    description = "Uniform bucket access flag"
    default = true
}
