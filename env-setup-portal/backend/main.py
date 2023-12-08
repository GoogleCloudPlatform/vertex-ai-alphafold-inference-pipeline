# Copyright 2022 Google LLC
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

# ======================== Loading basic libraries ===========================

import json
from time import sleep
from datetime import datetime, timezone
import os
import re
import uuid
import requests
from flask import Flask, request, render_template, flash, redirect, send_file, url_for, jsonify, session, Response
from authlib.integrations.flask_client import OAuth
from werkzeug.utils import secure_filename
from google.cloud import aiplatform as vertex_ai
from google.cloud import aiplatform_v1 as vertex_ai2
from google.cloud import storage
from flask_cors import CORS
import jwt
from kfp.v2 import compiler
import sys

sys.path.append('..')
from src.utils import fasta_utils
from src.utils import compile_utils

# Basic running parameters
PROJECT_ID = os.environ.get("PROJECT_ID")  # Change to your project ID
PROJECT_NUMBER = os.environ.get("PROJECT_NUMBER")  # Change to your project ID
ZONE = os.environ.get("ZONE")  # Change to your zone (example: us-central1-c)
BUCKET_NAME = os.environ.get("BUCKET_NAME")  # Change to your bucket name
FILESTORE_ID = os.environ.get("FILESTORE_ID") # Change to your Filestore ID
REGION = '-'.join(ZONE.split(sep='-')[:-1])
FILESTORE_SHARE = '/datasets'
AR_REPO_NAME = os.environ.get("AR_REPO_NAME")
FILESTORE_MOUNT_PATH = os.environ.get("FILESTORE_MOUNT_PATH") 
MODEL_PARAMS = f'gs://{BUCKET_NAME}'
IMAGE_URI = f'{REGION}-docker.pkg.dev/{PROJECT_ID}/{AR_REPO_NAME}/alphafold-components'

try :
    FILESTORE_IP, FILESTORE_NETWORK = compile_utils.get_filestore_info(
        project_id=PROJECT_ID, instance_id=FILESTORE_ID, location=ZONE)
except:
    print("WARNING - Filestore instance is not present. This will fail to run folding job.")

storage_client = storage.Client(project=PROJECT_ID)
vertex_ai.init(
    project=PROJECT_ID,
    location=REGION,
    staging_bucket=f'gs://{BUCKET_NAME}/staging'
)

#pip install --upgrade google-cloud-storage. 
def upload_to_bucket(blob_name, the_file, bucket_name):
    """ Upload data to a bucket"""
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob(blob_name)
    storage.blob._DEFAULT_CHUNKSIZE = 2097152 # 1024 * 1024 B * 2 = 2 MB
    storage.blob._MAX_MULTIPART_SIZE = 2097152 # 2 MB
    try:
        # content = the_file.read()
        blob.upload_from_filename(the_file)
        return f'gs://{BUCKET_NAME}/{blob_name}'
    except Exception as e:
        return f'FAILED to upload fasta file to GCS Bucket.\n{e}'
    

app = Flask(__name__)
CORS(app)

appConf = {
    "OAUTH2_CLIENT_ID": os.environ.get("OAUTH2_CLIENT_ID"), 
    "OAUTH2_CLIENT_SECRET": os.environ.get("OAUTH2_CLIENT_SECRET"), 
    "OAUTH2_META_URL" : "https://accounts.google.com/.well-known/openid-configuration",
    "FLASK_SECRET" : os.environ.get("FLASK_SECRET")
}

oauth = OAuth(app)
oauth.register("myApp",
               client_id=appConf.get("OAUTH2_CLIENT_ID"),
               client_secret=appConf.get("OAUTH2_CLIENT_SECRET"),
               server_metadata_url=appConf.get("OAUTH2_META_URL"),
               client_kwargs={
                   "scope": "openid profile email"
               }
               )
app.secret_key = appConf.get("FLASK_SECRET")

message = "" # global retun message

"""API Endpoints serving Alphafold UI Portal."""

@app.route("/", methods=['POST', 'GET'])
def AFportal():
    # Default static hosting that points to React's output
    return render_template('index.html')

@app.route("/check-fasta", methods=['POST'])
def check_fasta():
    if 'file' in request.files:
        f = request.files['file']
        filename = secure_filename(f.filename )
        # save file locally, for fasta validation purpose
        save_file_locally(f, filename)
        print(f"The to be checked filename was: {filename}")
        is_monomer, sequences = fasta_utils.validate_fasta_file(filename)
        return jsonify({
            "isMonomer": is_monomer,
            "residue": len(sequences)
        })
    return "no result"

def get_user_data(url, parameters):
        response = requests.get(url, params=parameters)
        if response.status_code == 200:
            return response.json()
        else:
            print(
                f"ERROR, here's a {response.status_code} error with your request")
            return None

def formatUrlLink(name, region, project_id):
    pipeline_run_name = name.split('/')[-1:][0]
    return f'https://console.cloud.google.com/vertex-ai/locations/{region}/pipelines/runs/{pipeline_run_name}?project={project_id}'

def formatUrlAllStructures(pipeline_name, bucket_name, exp_id, project_number):
    pipeline_run_name = pipeline_name.split('/')[-1:][0]
    return f'https://console.cloud.google.com/storage/browser/{bucket_name}/pipeline_runs/universal-pipeline-{exp_id}/{project_number}/{pipeline_run_name}'


@app.route("/clientid", methods=['GET'])
def get_clientid():
    return f'{os.environ.get("OAUTH2_CLIENT_ID")}'

def reformatBucketUri(gcs_uri):
    if gcs_uri is None:
        return "NA"
    folder = gcs_uri.replace("gs://","")
    folder = re.sub('[\w-]+\.[a-z]*', '', folder)
    return f'https://console.cloud.google.com/storage/browser/{folder}'

def extract_best_prediction_relaxation_url(_pipe, _client_pipeline, _status):
    get_request = vertex_ai2.GetPipelineJobRequest(name=_pipe.name) # pipe.name = pipeline ID
    pipeline_job = _client_pipeline.get_pipeline_job(get_request)
    predict_tasks = [i for i in pipeline_job.job_detail.task_details if i.task_name == 'predict']

    formated_predict_tasks = []

    for t in predict_tasks:
        task_id = t.task_id
        parent_task_id = t.parent_task_id
        model_name = t.execution.metadata['input:model_name']
        ranking_confidence = 0 if t.outputs["raw_prediction"].artifacts[0].metadata.get("ranking_confidence") == None else t.outputs['raw_prediction'].artifacts[0].metadata['ranking_confidence']
        uri = t.outputs['raw_prediction'].artifacts[0].uri

        formated_predict_tasks.append(
            {
                'task_id': task_id,
                'parent_task_id': parent_task_id,
                'model_name': model_name,
                'ranking_confidence': ranking_confidence,
                'uri': uri
            }
        )

    # Sort predict tasks by ranking confidence
    sorted_predict = sorted(formated_predict_tasks, key=lambda x: x['ranking_confidence'], reverse=True)

    top_predict_uri = None
    top_relax_uri = None

    if _status != "RUNNING":
        # Get top prediction
        if len(sorted_predict) > 0:
            top_predict_uri = None if sorted_predict[0].get("uri") == None else sorted_predict[0]["uri"]
            top_predict_uri = top_predict_uri if ".pkl" in top_predict_uri else None

            # Get top relaxation
            condition_relax_parent_id = None
            for t in pipeline_job.job_detail.task_details:
                if t.parent_task_id == sorted_predict[0]['parent_task_id'] and 'condition' in t.task_name:
                    condition_relax_parent_id = t.task_id
                    break
            for t in pipeline_job.job_detail.task_details:
                if t.parent_task_id == condition_relax_parent_id:
                    top_relax_uri = t.outputs['relaxed_protein'].artifacts[0].uri
                    break

    return [reformatBucketUri(top_predict_uri), reformatBucketUri(top_relax_uri)]

@app.route("/status", methods=['GET'])
def get_dashboarddata():
    user_info = valid_user()

    if user_info is not None:
        API_ENDPOINT = "{}-aiplatform.googleapis.com".format(REGION)
        # Create Pipelines and Metadata service clients
        client_pipeline = vertex_ai2.PipelineServiceClient(client_options={"api_endpoint": API_ENDPOINT})
        client_metadata = vertex_ai2.MetadataServiceClient(client_options={"api_endpoint": API_ENDPOINT})
        list_pipelines_request = vertex_ai2.ListPipelineJobsRequest(parent=f'projects/{PROJECT_ID}/locations/{REGION}')
        list_pipelines = list(client_pipeline.list_pipeline_jobs(list_pipelines_request))
        running_pp = []
        
        for pipe in list_pipelines:
            labels = pipe.labels
            status = pipe.state.name.split("_")[-1]
            url_link = formatUrlLink(pipe.name, REGION, PROJECT_ID)
            url_all_structures = formatUrlAllStructures(pipe.name, BUCKET_NAME, labels['experiment_id'], PROJECT_NUMBER)

            # Extract metadata about prediction ranking (best)
            predict_relax_uri = extract_best_prediction_relaxation_url(pipe, client_pipeline, status)
            if pipe.end_time:
                duration = pipe.end_time - ( pipe.end_time if pipe.start_time is None else pipe.start_time)
            else:
                duration = datetime.now(timezone.utc) - pipe.start_time

            seconds = duration.total_seconds()
            hours = int(seconds // 3600)
            minutes = int((seconds % 3600) // 60)
            seconds = seconds % 60
            ti = f'{hours}h{minutes}m'
            p_data ={
                "run_tag": labels['run_tag'],
                "experiment_id":labels['experiment_id'],
                "sequence":labels['sequence_id'],
                "status":status,
                "duration":ti,
                "url_link": url_link,
                "url_all_structures": url_all_structures,
                "top_predict_uri": predict_relax_uri[0], # first index is predict URL
                "top_relax_uri": predict_relax_uri[1],
                "user": labels['user']
            }
            running_pp.append(p_data)
        return jsonify(running_pp)
    else:
        return Response("{'status':'Unauthorized'}", status=401, mimetype='application/json')

def valid_user():
    headers = request.headers
    bearer = headers.get('Authorization')
    token = bearer.split()[1]

    GOOGLE_TOKEN_INFO_ENDPOINT = "https://oauth2.googleapis.com/tokeninfo"
    parameters = { "id_token": token}
    user_info = get_user_data(GOOGLE_TOKEN_INFO_ENDPOINT, parameters)
    # check for 1.Hashed email match 2.Expiry token 3.Non Empty
    if user_info is not None:
        # check token expiry
        if datetime.now().timestamp() > float(user_info['exp']): return None
    return user_info

def decide_accelerator_type(machine_type):
    if machine_type.startswith("a"):
        return "NVIDIA_TESLA_A100"
    elif machine_type.startswith("g"):
        return "NVIDIA_L4"
    else:
        return "NVIDIA_L4"

@app.route("/fold",methods=['POST'])
def fold():
    user_info = valid_user()
    if user_info is not None:
        #  check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return Response('{"status":"uploaded file missing."}',status=400, mimetype='application/json')
        f = request.files['file']

        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        form = dict(request.form)
        print(f"Folding request received on {timestamp}, with parameters {form}")
        # Saving the received file to local disk

        filename = secure_filename(f.filename )
        print(f"The received filename was: {filename}")

        # Copying the received file to cloud storage and saving the path
        gcs_sequence_path = f'fasta/{filename}' # TODO add username subfolder

        # save file locally, for fasta validation purpose
        save_file_locally(f, filename)
        gcs_path = upload_to_bucket(gcs_sequence_path,filename,BUCKET_NAME)
        print(f"Protein file uploaded to: {gcs_path}")

        # is_monomer, sequences = fasta_utils.validate_fasta_file_gcs(gcs_path,gcs_sequence_path,BUCKET_NAME,storage_client)
        is_monomer, sequences = fasta_utils.validate_fasta_file(filename)
        # TODO delete local disk fasta file after validate
        print(f'IS MONOMER {is_monomer}\n{sequences}')

        # Capturing the running parameters of the pipeline
        params = {
        'sequence_path': gcs_path,
        'max_template_date': '2030-01-01',
        'use_small_bfd': True if form["smallBFD"] == "yes" else False,
        'num_multimer_predictions_per_model': int(form["predictionCount"]),
        'is_run_relax': 'relax' if str(form["relaxation"]).lower() == "yes" else '', 
        'model_preset': str(form["proteinType"]).lower(),
        'project': PROJECT_ID,
        'region': REGION
        }

        os.environ['PREDICT_MACHINE_TYPE'] = str(form["predictMachineType"]).lower()
        os.environ['PREDICT_ACCELERATOR_COUNT'] = str(form["acceleratorCount"]).lower()
        os.environ['PREDICT_ACCELERATOR_TYPE'] = decide_accelerator_type(str(form["predictMachineType"]))
        
        os.environ['RELAX_MACHINE_TYPE'] = str(form["relaxMachineType"]).lower()
        os.environ['RELAX_ACCELERATOR_COUNT'] = str(form["relaxAcceleratorCount"]).lower()
        os.environ['RELAX_ACCELERATOR_TYPE'] = decide_accelerator_type(str(form["relaxMachineType"]))

        os.environ['ALPHAFOLD_COMPONENTS_IMAGE'] = IMAGE_URI
        os.environ['NFS_SERVER'] = FILESTORE_IP
        os.environ['NFS_PATH'] = FILESTORE_SHARE
        os.environ['NETWORK'] = FILESTORE_NETWORK
        os.environ['MODEL_PARAMS_GCS_LOCATION'] = MODEL_PARAMS
        os.environ['PARALLELISM'] = '5'
        
        # Compile the pipeline
        from src.pipelines.alphafold_inference_pipeline import alphafold_inference_pipeline as pipeline
        run_tag = str(form["runTag"]).lower()
        experiment_id = str(form["experimentId"]).lower()
        pipeline_name = f'universal-pipeline-{experiment_id}'
        compiler.Compiler().compile(
            pipeline_func=pipeline,
            package_path=f'{pipeline_name}.json')

        # Run FOLD
        # Running the existing pipeline
        labels = {'run_tag': run_tag
                 ,'experiment_id': experiment_id
                 , 'sequence_id': filename.split(sep='.')[0].lower()
                 , 'user': f'{user_info["given_name"].lower()}_{user_info["family_name"].lower()}'
                 }

        pipeline_job = vertex_ai.PipelineJob(
            display_name=pipeline_name,
            template_path=f'{pipeline_name}.json', # pipeline name need to be unique, and subfolders in GCS
            pipeline_root=f'gs://{BUCKET_NAME}/pipeline_runs/{pipeline_name}',
            parameter_values=params,
            enable_caching=True,
            labels=labels)
        pipeline_job.run(sync=False)
        pipeline_job.wait_for_resource_creation()

        # Log folding job
        message = f"Folding started for experiment ID {experiment_id} with parameters {params}"
        print(f'/fold MESAGE {message}')
        return Response("status: folding is in progress... }", 
                        status=200,mimetype='application/json') 
    else:
        return Response("{'status':'Unauthorized'}", status=401, mimetype='application/json')

def save_file_locally(f, filename):
    with open (f'{filename}','wb') as file:
        content = f.read()
        file.write(content)
    sleep(3)
    

# ======= Server initialization (listening)
if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))