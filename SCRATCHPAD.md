
export PROJECT_ID=jk-mlops-dev
export PIPELINE_PATH=pipelines/alphafold_inference_pipeline.py
export PACKAGE_PATH=alphafold_inference_pipeline.json
export FUN_NAME=alphafold_inference_pipeline
export ALPHAFOLD_COMPONENTS_IMAGE=gcr.io/$PROJECT_ID/alphafold-components
export NFS_SERVER=10.130.0.2
export NFS_PATH=/datasets
export NETWORK=projects/895222332033/global_networks/jk-af-dev-network
export MODEL_PARAMS_GCS_LOCATION=gs://jk-af-dev-bucket


dsl-compile --py $PIPELINE_PATH --function $FUN_NAME --output $PACKAGE_PATH


python compile.py \
--project=jk-mlops-dev \
--filestore_instance_id=jk-af-dev-fs \
--filestore_instance_location=us-central1-a \
--filestore_share="/datasets" \
--predict_gpu=nvidia-tesla-t4 \
--relax_gpu=nvidia-tesla-t4 \
--pipeline_fun=src.pipelines.alphafold_inference_pipeline.alphafold_inference_pipeline \
--pipeline_package_path=alphafold_inference_pipeline.json


python run.py \
--project=jk-mlops-dev \
--region=us-central1 \
--staging_bucket=gs://jk-alphafold-staging \
--pipelines_sa="pipelines-sa@jk-mlops-dev.iam.gserviceaccount.com" \
--pipeline_template_path="alphafold_inference_pipeline.json" \
--experiment_id=test_ex_1 \
--params=\
sequence_path=../../sequences/T1050.fasta,\
max_template_date=2020-05-14,\
model_preset=monomer,\
project=jk-mlops-dev,\
region=us-central1,\
use_small_bfd=True,\
num_multimer_predictions_per_model=5,\
is_run_relax=True


