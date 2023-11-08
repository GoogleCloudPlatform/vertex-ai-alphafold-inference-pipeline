# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

provider "google" {
  project = var.project_id
  region  = var.region
}   

data "google_project" "gcp_project_info" {
  project_id = var.project_id
}

// Enable required APIs
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

### Create Service Account for the tool and assign roles/permissions

resource "google_service_account" "cloud_run_sa" {
  account_id  = "${var.cloud_run_service_name}-cr"
  project     = var.project_id
  description = "SA for Alphafold Portal Cloud Run"
  depends_on  = [google_project_service.enable_required_services]
}

resource "google_project_iam_member" "assign_sa_roles" {
  for_each = toset([
    "roles/file.editor",
    "roles/run.admin",
    "roles/storage.objectAdmin",
    "roles/aiplatform.serviceAgent",
    "roles/aiplatform.user"
  ])
  role    = each.key
  member = "serviceAccount:${google_service_account.cloud_run_sa.email}"
  project = var.project_id
}

locals {
  service_image_tag = "${var.region}-docker.pkg.dev/${var.project_id}/${var.ar_repo_name}/${var.cloud_run_service_name}:latest" 
}

## Provide Cloud Build Service Account AR write Access
resource "google_project_iam_member" "set_cloud_build_sa_permissions" {
  member   = "serviceAccount:${data.google_project.gcp_project_info.number}@cloudbuild.gserviceaccount.com"
  project  = var.project_id
  role     = each.key
  for_each = toset([
    "roles/artifactregistry.writer"
  ])
}

resource "null_resource" "build_alphafold_portal_cr_image" {

  triggers = {
    full_image_path = local.service_image_tag
  }

  provisioner "local-exec" {
    when    = create
    command = <<-EOT
      gcloud builds submit . \
      --region=${var.region} \
      --project=${var.project_id} \
      --config=alphafold-cloudbuild.yml \
      --substitutions=_CONTAINER_IMAGE_TAG=${local.service_image_tag} \
      --ignore-file=./.dockerignore
      EOT
  }

  provisioner "local-exec" {
    when    = destroy
    command = <<-EOT
      gcloud artifacts docker images delete \
      ${self.triggers.full_image_path} \
      --quiet
      EOT
  }
}

resource "google_cloud_run_v2_service" "alphafold_portal" {
  depends_on = [
    null_resource.build_alphafold_portal_cr_image
  ]

  name     = var.cloud_run_service_name
  project  = var.project_id
  location = var.region

  template {
    service_account       = google_service_account.cloud_run_sa.email
    execution_environment = "EXECUTION_ENVIRONMENT_GEN2"
    containers {
      image = local.service_image_tag

      env {
        name  = "OAUTH2_CLIENT_ID"
        value = var.oauth2_client_id
      }
      env {
        name  = "OAUTH2_CLIENT_SECRET"
        value = var.oauth2_client_secret
      }
      env {
        name  = "FLASK_SECRET"
        value = var.flask_secret
      }
      env {
        name  = "PROJECT_ID"
        value = var.project_id
      }
      env {
        name  = "PROJECT_NUMBER"
        value = data.google_project.gcp_project_info.number
      }
      env {
        name  = "ZONE"
        value = var.zone
      }
      env {
        name  = "BUCKET_NAME"
        value = var.gcs_bucket_name
      }
      env {
        name  = "AR_REPO_NAME"
        value = var.ar_repo_name
      }
      env {
        name  = "FILESTORE_ID"
        value = var.filestore_instance_id
      }
      env {
        name  = "FILESTORE_MOUNT_PATH"
        value = "/mnt/nfs/alphafold"
      }
      env {
        name  = "PREDICT_MACHINE_TYPE"
        value = var.machine_type
      }
      env {
        name  = "PREDICT_ACCELERATOR_COUNT"
        value = var.predict_accelerator_count
      }
    }
  }
}

## Make the Cloud Run Unauthenticated

data "google_iam_policy" "noauth_policy" {
  binding {
    role    = "roles/run.invoker"
    members = [
      "allUsers",
    ]
  }
}

resource "google_cloud_run_v2_service_iam_policy" "noauth_policy_for_app" {
  project     = var.project_id
  location    = var.region
  name        = google_cloud_run_v2_service.alphafold_portal.name
  policy_data = data.google_iam_policy.noauth_policy.policy_data
}
