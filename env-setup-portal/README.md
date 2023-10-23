## Prerequisites
   In order to install Alphafold Portal, setup Alphafold Inference Pipeline first. Refer to the installation guide: https://github.com/GoogleCloudPlatform/vertex-ai-alphafold-inference-pipeline/blob/main/README.md

   This guide assumes that Artifact Registry repository from the above tutorial has been setup. The location should follow this format:
   
   ```
   ${REGION}-docker.pkg.dev/${PROJECT_ID}/${AR_REPO_NAME}/alphafold-components
   ```
   

### Create OAuth Consent Screen
   Follow the steps as per https://developers.google.com/identity/gsi/web/guides/get-google-api-clientid to generate a Client ID.
   
   ```shell
   CLIENT_ID="<replace_with_generated_client_id>"
   CLIENT_SECRET="<replace_with_generated_client_secret>"
   ```

### Populate terraform.tfvars File Default Values

```
oauth2_client_id        = "<CLIENT_ID from OAuth Screen Setup>"
oauth2_client_secret    = "<CLIENT_SECRET from OAuth Screen Setup>"
flask_secret            = "<any random string, use https://www.uuidgenerator.net/guid"
project_id              = "<PROJECT_ID>"
region                  = "<REGION>"
zone                    = "<ZONE>"
filestore_instance_id   = "<FILESTORE_INSTANCE_ID>"
bucket_name             = "<GCS_BUCKET_NAME>"
ar_repo_name            = "<ARTIFACT_REGISTRY_REPO_NAME>"
```

### Apply Terraform

Assuming the current working directly is at `~/vertex-ai-alphafold-inference-pipeline`

```
cd env-setup-portal
terraform init
terraform apply
```

### Add the Cloud Run Generated URL into Authorized Domains in OAuth Consent Screen

Once terraform apply command success, there will be a URL of the cloud run instance that being created:

```
alphafold_portal_cloud_run_uri=https://SOME_URL
```

Copy the URL and add the URL into OAuth Consent Screen's Authorized Javascript origins
*and* Authorized redirect URIs section, with additional redirect path: `/api/auth/callback/google`

For example: 

Section Autorized Javascript origins

```
http://some_url
```

Section Authorized redirect URIs

```
http://some_url/api/auth/callback/google
```

### Accessing Alphafold Portal

Simply access the generated Cloud Run's URL, ex: `https://some_url``