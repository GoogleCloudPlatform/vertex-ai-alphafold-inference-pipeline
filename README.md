# AlphaFold batch inference with Vertex AI Pipelines

This repository compiles prescriptive guidance and code samples demonstrating how to operationalize AlphaFold batch inference using Vertex AI Pipelines. 

Code sample base on v2.3.1 of AlphaFold.

## Solutions architecture overview

The following diagram depicts the architecture of the solution.

![Architecture](/images/alphafold-vertex-v1.png)

Key design patterns:

- Inference pipelines are implemented using [Kubeflow Pipelines (KFP) SDK v2](https://www.kubeflow.org/docs/components/pipelines/sdk-v2/) 
- Feature engineering, model inference, and protein relaxation steps of AlphaFold inference are encapsulated in reusable KFP components
- Whenever optimal, inference steps are run in parallel
- Each step runs on the most optimal hardware platform. E.g. data preprocessing steps run on CPUs while model predictions and structure relaxations run on GPUs
- High performance NFS file system - Cloud Filestore - is used to manage genetic databases used during the inference workflow
- Artifacts and metadata created during pipeline runs are tracked in Vertex ML Metadata supporting robust experiment management and analysis.

The core of the solution is a set of parameterized KFP components that encapsulate key tasks in the AlphaFold inference workflow. The AlphaFold KFP components can be composed to implement optimized inference workflows. Currently, the repo contains two example pipelines:
- [Universal pipeline](src/pipelines/alphafold_inference_pipeline.py). This pipeline mirrors the functionality and settings of the [AlphaFold inference script](https://github.com/deepmind/alphafold/blob/main/run_alphafold.py) but optimizes elapsed time and compute resources utilization. The pipeline orchestrates the inference workflow using three discrete tasks: feature engineering, model prediction, and protein relaxation. The feature engineering task wraps the [AlphaFold data pipelines](https://github.com/deepmind/alphafold/tree/main/alphafold/data). The model prediction, and protein relaxation wrap the [AlphaFold model runner](https://github.com/deepmind/alphafold/blob/main/alphafold/model/model.py) and the [AlphaFold Amber relaxation](https://github.com/deepmind/alphafold/tree/main/alphafold/relax). The feature engineering task is run on a CPU-only compute node. The model predict and relaxation steps are run on GPU compute nodes. The model predict and relaxation steps are parallelized. For example, for a monomer scenario with the default settings, the pipeline will start 5 model predict operations in parallel on 5 GPU nodes.
![Universal pipeline](/images/universal-pipeline.png)
- [Monomer optimized pipeline](src/pipelines/alphafold_optimized_monomer.py). The *Monomer optimized pipeline* demonstrates how to further optimize the inference workflow by parallelizing feature engineering steps. The pipeline uses KFP components that encapsulate genetic database search tools (*hhsearch, jackhmmer, hhblits*, etc) to execute database searches in parallel. Each tool runs on the most optimal CPU platform. For example, *hhblits* and *hhsearch* tools are run on C2 series machines that feature Intel processors with the AVX2 instruction set, while *jackhmmer* runs on an N2 series machine. This pipeline only supports folding monomers.
![Monomer pipeline](/images/monomer-pipeline.png)

The repository also includes a set of Jupyter notebooks that demonstrate how to configure, submit, and analyze pipeline runs.

## Repository structure

`src/components` -  KFP components encapsulating AlphaFold inference tasks

`src/pipelines` -  Example inference pipelines 

`env-setup` - Terraform for setting up a sandbox environment

`*.ipynb` - Jupyter notebooks demonstrates how to configure and run the inference pipeline.


## Managing genetic databases

AlphaFold inference utilizes a set of [genetic databases](https://github.com/deepmind/alphafold#genetic-databases). To maximize database search performance when running multiple inference pipelines concurrently, the databases are hosted on a high performance NFS file share managed by [Cloud Filestore](https://cloud.google.com/filestore).

Before running the pipelines you need to configure a Cloud Filestore instance and populate it with genetic databases.

The **Environment requirements** section describes how to configure the GCP environment required to run the pipelines, including Cloud Filestore configuration. 

The repo also includes an [example Terraform configuration](/env-setup) that builds a sandbox environment meeting the requirements. If you intend to use the provided Terraform configuration you need to pre-stage the genetic databases and model parameters in a Google Cloud Storage bucket. When the Terraform configuration is applied, the databases will be copied from the GCS bucket to the provisioned Filestore instance and the model parameters will be copied to the provisioned regional GCS bucket.

Follow [the instructions on the AlphaFold repo](https://github.com/deepmind/alphafold#genetic-databases) to download the genetic databases and model parameters. 

**Notes: Once you Make sure to download both the full size and the reduced version of BFD. The total download size for the full databases is around 556 GB and the total size when unzipped is 2.62 TB.**

These are the minimum commands required:
```bash
sudo apt install aria2
scripts/download_all_data.sh <DOWNLOAD_DIR>
scripts/download_small_bfd.sh <DOWNLOAD_DIR>
```

## Environment requirements

The below diagram summarizes Google Cloud environment configuration required to run AlphaFold inference pipelines.

![Infrastructure](/images/alphafold-infra.png)


- All services should be provisioned in the same project and the same compute region
- To maintain high performance access to genetic databases, the database files are stored on an instance of Cloud Filestore. To integrate the instance with Vertex AI services the following configuration is required:
    - A Filestore instance should be provisioned on a VPC that is [peered to the Google services network](https://cloud.google.com/vpc/docs/private-services-access).
    - A Filestore instance should be provisioned with the `connect-mode` setting [set to `PRIVATE_SERVICE_ACCESS`](https://cloud.google.com/filestore/docs/creating-instances#gcloud)
    - An NFS file share that hosts genetic databases must be accessible without authentication
    - All genetic databases [referenced on the AlphaFold repo](https://github.com/deepmind/alphafold#genetic-databases), *including both a full and a reduced size BFD*, should be copied to the file share. The database files can be arranged in any folder layout. However, if possible, we recommend using the same directory structure as described on the AlphaFold repo, as this is the default configuration of example inference pipelines. Note that if the different directory structure is preferable the pipelines can be easily modified.
- Vertex Pipelines should be used with [a custom service account](https://cloud.google.com/vertex-ai/docs/general/custom-service-account). The account should be provisioned with the following role settings:
    - `storage.admin`
    - `aiplatform.user`
- An instance of Vertex Workbench is used as a development environment to customize pipelines and submit and analyze pipeline runs. The instance should be provisioned on the same VPC as the instance of Filestore.
- A regional GCS bucket located in the same region as Vertex AI services is used to managed artifacts created by pipelines. 
- AlphaFold model parameters should be copied to the regional bucket. The pipelines assume that the parameters can be retrieved from the bucket. The default location for the parameters configured in the pipelines is `gs://<BUCKET_NAME>/params`. 



## Quick-start Guide

The repo includes a Terraform configuration that can be used to provision a sandbox environment that complies with the requirements detailed in the previous section. The configuration builds the sandbox environment as follows:
- Creates a VPC and a subnet to host a Filestore instance and a Vertex Workbench instance
- Configures VPC Peering between the VPC and the Google services network
- Creates a Filestore instance
- Creates a regional GCS bucket
- Creates a Vertex Workbench instance 
- Creates service accounts for Vertex AI
- Copies the genetic databases from a pre-staging GCS location to the Filestore file share
- Copies the AlphaFold model parameters from a pre-staging GCS location to the provisioned regional GCS bucket

You need to have "Owner" privileges to set up the sandbox environment.

You will be using [Cloud Shell](https://cloud.google.com/shell/docs/using-cloud-shell) to deploy the infrastructure by applying the Terraform configuration. 

### Step 1 - Select a Google Cloud project and open Cloud Shell

In the Google Cloud Console, navigate to your project and open [Cloud Shell](https://cloud.google.com/shell/docs/using-cloud-shell). ***Make sure you have Owner privileges***.

### Step 2 - Enable the required services

Run the following commands to enable the required services.

```bash
export PROJECT_ID=<YOUR PROJECT ID>
```

```bash
gcloud config set project $PROJECT_ID

gcloud services enable \
cloudbuild.googleapis.com \
compute.googleapis.com \
cloudresourcemanager.googleapis.com \
iam.googleapis.com \
container.googleapis.com \
cloudtrace.googleapis.com \
iamcredentials.googleapis.com \
monitoring.googleapis.com \
logging.googleapis.com \
notebooks.googleapis.com \
aiplatform.googleapis.com \
file.googleapis.com \
servicenetworking.googleapis.com

```


### Step 3 - Apply the Terraform configuration


First, clone the repo.

```bash
git clone https://github.com/GoogleCloudPlatform/vertex-ai-alphafold-inference-pipeline.git
cd vertex-ai-alphafold-inference-pipeline/env-setup
```

Set the below environment variables to reflect your environment. The Terraform will attempt to create new resources so make sure that the resources with the specified names do not already exist. 

- `REGION` - your compute region
- `ZONE` - your compute zone
- `NETWORK_NAME` - the name for the VPC network
- `SUBNET_NAME` - the name for the VPC network
- `WORKBENCH_INSTANCE_NAME` - the name for the Vertex Workbench instance
- `FILESTORE_INSTANCE_ID` - the instance ID of the Filestore instance. See [Naming your instance](https://cloud.google.com/filestore/docs/creating-instances#naming_your_instance)
- `GCS_BUCKET_NAME` - the name of the GCS regional bucket. See [Bucket naming guidelines](https://cloud.google.com/storage/docs/naming-buckets) 
- `GCS_DBS_PATH` - the path to the GCS location of the genetic databases and model parameters. Terraform will copy the databases replicating a folder structure on GCS. Terrafom will also copy model parameters to the regional bucket. The parameters should be in the `<GCS_DBS_PATH>/params`


```bash
export REGION=<YOUR REGION>
export ZONE=<YOUR ZONE>
export NETWORK_NAME=<YOUR NETWORK NAME>
export SUBNET_NAME=<YOUR SUBNET NAME>
export WORKBENCH_INSTANCE_NAME=<YOUR WORKBENCH INSTANCE NAME>
export FILESTORE_INSTANCE_ID=<YOUR INSTANCE ID>
export GCS_BUCKET_NAME=<YOUR BUCKET NAME>
export GCS_DBS_PATH=<YOUR GCS LOCATION FOR GENETIC DBS>
```


Apply Terraform configuration. This step may take a few minutes so be patient.

```bash
terraform init
terraform apply \
-var=project_id=$PROJECT_ID \
-var=region=$REGION \
-var=zone=$ZONE \
-var=network_name=$NETWORK_NAME \
-var=subnet_name=$SUBNET_NAME \
-var=workbench_instance_name=$WORKBENCH_INSTANCE_NAME \
-var=filestore_instance_id=$FILESTORE_INSTANCE_ID \
-var=gcs_bucket_name=$GCS_BUCKET_NAME \
-var=gcs_dbs_path=$GCS_DBS_PATH

```

In addition to provisioning and configuring the required services, the Terraform configuration starts a Vertex Training job that copies the reference databases from the GCS location to the provisioned Filestore instance. You can monitor the job using the links printed out by Terraform. The job may take a couple of hours to complete.

**Note that the terraform state is created and stored in your private Cloud Shell disk. It means that only your user is able to maintain the deployed infrastructure via Terraform commands, including destroying this quick-start installation. Don't move or delete the terraform state file, called `env-setup/terraform.tfstate` before reading the official Terraform documentation**


### Step 4. Build the container image that encapsulates custom KFP components used by the inference pipeline


```bash
PROJECT_ID=$(gcloud config list --format 'value(core.project)')
IMAGE_URI=gcr.io/${PROJECT_ID}/alphafold-components

cd vertex-ai-alphafold-inference-pipeline
gcloud builds submit --timeout "2h" --tag ${IMAGE_URI} . --machine-type=e2-highcpu-8
```


### Step 5. Preparing Vertex Workbench

In the GCP project, a Vertex Workbench user-managed notebook instance is used as a development/experimentation environment to customize, submit, and analyze inference pipelines runs. There are a couple of setup steps that are required before you can use example notebooks.

Open Vertex AI Workbench, connect to the notebook instance clicking on the "OPEN JUPYTERLAB" link besides the notebook name.

On the JupyterLab interface, launch a new Terminal tab and execute the following command:

```bash
git clone https://github.com/GoogleCloudPlatform/vertex-ai-alphafold-inference-pipeline.git
```

### Congratulations!

Now, you're ready to follow the instructions on the notebook "1-alphafold-quick-start.ipynb".


## Clean up

In case you want to destroy all the deployed infrastructure, follow this instruction. 

**Note that all infrastructure will be destroyed including any changes you have done in the code inside the Vertex Workbench notebook instance. Make sure you commit all your changes before executing this step.**

Back in the Google Cloud Console, open [Cloud Shell](https://cloud.google.com/shell/docs/using-cloud-shell) and execute the following commands.

```bash
cd ~/vertex-ai-alphafold-inference-pipeline/env-setup

terraform destroy \
-var=project_id=$PROJECT_ID \
-var=region=$REGION \
-var=zone=$ZONE \
-var=network_name=$NETWORK_NAME \
-var=subnet_name=$SUBNET_NAME \
-var=workbench_instance_name=$WORKBENCH_INSTANCE_NAME \
-var=filestore_instance_id=$FILESTORE_INSTANCE_ID \
-var=gcs_bucket_name=$GCS_BUCKET_NAME \
-var=gcs_dbs_path=$GCS_DBS_PATH
```
