## Prerequisites
   In order to install Alphafold Portal, setup Alphafold Inference Pipeline first. Refer to the installation guide: https://github.com/GoogleCloudPlatform/vertex-ai-alphafold-inference-pipeline/blob/main/README.md

   This guide assumes that Artifact Registry repository from the above tutorial has been setup. The location should follow this format:
   
   ```sh
   ${REGION}-docker.pkg.dev/${PROJECT_ID}/${AR_REPO_NAME}/alphafold-components
   ```
   

### Create OAuth Consent Screen
   Follow the steps as per https://developers.google.com/identity/gsi/web/guides/get-google-api-clientid to generate a CLIENT_ID and CLIENT_SECRET. Alternatively follow the following steps:

1. Go to OAuth Consent Screen Page in the browser:
   ```
   https://console.cloud.google.com/apis/credentials/consent?referrer=search&project=<YOUR PROJECT_ID>
   ```

2. Choose Internal for User Type, then click **Create**.
3. Fill only the mandatory fields, then click **Save and Continue**.

   > Note: For Authorized Domain section you may leave it empty first until the Cloud Run URL (alphafold_portal_cloud_run_uri, refer below) is generated. Authorized Domain is auto-populated when Authorized Javascript Origin is filled in.

4. On Scope page, leave everything as is and click **Save and Continue**.
5. On Summary page, click **Back to Dashboard**.
6. Go to Credentials page: https://console.cloud.google.com/apis/credentials?project=<YOUR PROJECT_ID>
7. Click **Create Credentials**, and choose _OAuth Client ID_
8. Choose Web Application from **Application Type** dropdown.
9. Type any name to identify the client, ex: _alpha_portal_client_, then click **Create**
10. Copy the generated **Client ID** and **Client Secret** and export them as environment variables:
   
   ```sh
   CLIENT_ID="<replace_with_generated_client_id>"
   CLIENT_SECRET="<replace_with_generated_client_secret>"
   ```
   > Note: Leave Authorized Javascript Origin and Redirect URI section empty for now until the terraform is deployed and `alphafold_portal_cloud_run_uri` (Cloud Run URL) is generated.


### Populate terraform.tfvars File Default Values

Assuming the copy of the repo is at `~/vertex-ai-alphafold-inference-pipeline/`, copy the terraform.tfvars from env-setup/ folder to env-setup-portal/ folder:

```
cp ~/vertex-ai-alphafold-inference-pipeline/env-setup/terraform.tfvars ~/vertex-ai-alphafold-inference-pipeline/env-setup-portal
cd ~/vertex-ai-alphafold-inference-pipeline/env-setup-portal
```

Make sure the copied or the newly generated terraform.tfvars file contains minmimally these variables:

```
project_id              = "<PROJECT_ID>"
region                  = "<REGION>"
zone                    = "<ZONE>"
filestore_instance_id   = "<FILESTORE_INSTANCE_ID>"
gcs_bucket_name         = "<GCS_BUCKET_NAME>"
ar_repo_name            = "<ARTIFACT_REGISTRY_REPO_NAME>"
oauth2_client_id        = "<CLIENT_ID from OAuth Screen Setup>"
oauth2_client_secret    = "<CLIENT_SECRET from OAuth Screen Setup>"
flask_secret            = "<any random string, use https://www.uuidgenerator.net/guid"
```

### Apply Terraform

Assuming the current working directly is at `~/vertex-ai-alphafold-inference-pipeline`

```sh
cd env-setup-portal
terraform init
terraform apply
```

### Add the Cloud Run Generated URL into OAuth Consent Screen

Once terraform apply command success, there will be a URL of the cloud run instance that being created:

```
alphafold_portal_cloud_run_uri=https://SOME_URL
```

Add the Authorized Javascript Origins and Authorized redirect URIs in Client ID Configuration Page:
S
```sh
echo "https://console.cloud.google.com/apis/credentials/oauthclient/${CLIENT_ID}?project=${PROJECT_ID}"
```
> Note: Open the link at the output of `echo` command


Copy the URL (alphafold_portal_cloud_run_uri's value) and add the URL into OAuth Consent Screen's Authorized Javascript origins
*and* Authorized redirect URIs section, with additional redirect path: `/api/auth/callback/google`

For example: 

Section Authorized Javascript origins

```
http://SOME_URL
```

Section Authorized redirect URIs

```
http://SOME_URL/api/auth/callback/google
```


### Accessing Alphafold Portal

Simply access the generated Cloud Run's URL, ex: `https://SOME_URL``

### Troubleshooting

Upon login, the address bar might show pop-up being blocked, or error message shown in the page. Please allow pop-up window for the suggested URL and retry.