/**
 * Copyright 2024 Google LLC
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *      http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

terraform {
  required_version = ">= 1.5"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.44"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 6.8"
    }
    local = {
      source = "hashicorp/local"
      version = "~> 2.5"
    }
    null = {
      source = "hashicorp/null"
      version = "~> 3.2"
    }
    random = {
      source = "hashicorp/random"
      version = "~> 3.6"
    }
    external = {
      source = "hashicorp/external"
      version = "~> 2.3"
    }
  }

  provider_meta "google" {
    module_name = "cloud-solutions/alphafold-inference-pipeline-v1.0"
  }
}

provider "google" {
      user_project_override = true
}
provider "google-beta" {
      user_project_override = true
}