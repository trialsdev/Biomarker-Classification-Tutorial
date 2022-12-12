import base64
import json
import os
import pandas as pd
import numpy as np
import zipfile

from flask import Flask, request

from google.cloud import storage

from prepare_data import prepare_images

from predict import predict_images

#storage client instance
storage_client = storage.Client()

#helper functions
def receive_data(data):
    """
    download the zip file and extract the files to the data folder.
    """
    #input bucket instance
    file_data = data
    input_bucket_name = file_data["bucket"]
    output_bucket_name = input_bucket_name.replace('input', 'output')

    #get file
    input_file_name = file_data["name"]
    input_bucket = storage_client.get_bucket(input_bucket_name)
    zip_blob = input_bucket.get_blob(input_file_name)

    #download zip file from input bucket
    with open("input_zip.zip", "wb") as zip_file:
        zip_file.write(zip_blob.download_as_bytes())

    #extract the zip files to the data folder
    with zipfile.ZipFile("input_zip.zip", "r") as zip_ref:
        zip_ref.extractall('data/dicom')
    
    #list extracted file names
    file_names = os.listdir('data/dicom')
    print(file_names)

    #create dataframe
    # df = pd.DataFrame(columns = ['File_Name', 'Prediction'])
    # df['File_Name'] = file_names

    print(f'Recieved data from {input_bucket_name}')
    return output_bucket_name, input_file_name

def create_pngs():

    prepare_images('data/dicom/', 'data/images/')
    print('Created PNG files')

def upload_data(file_name, output_bucket_name, input_file_name):
    """
    Upload the CSV file to the output bucket
    """
    #output file name
    output_file_name = f"predictions_{input_file_name}.csv"

    #output bucket instance
    output_bucket = storage_client.get_bucket(output_bucket_name)
    output_blob = output_bucket.blob(output_file_name)

    ## upload file to output bucket
    with open(str(file_name), "rb") as output_file:
        output_blob.upload_from_file(output_file)

    print(f'uploaded file to {output_bucket_name}')
    
def run_inference(data):
    """
    Run inference on the images given new data.
    """
    #recieve data from storage bucket and get the csv with file names
    output_bucket_name, input_file_name = receive_data(data)

    #create the png files
    create_pngs()

    #get model predictions
    df = predict_images('data/images/')

    #save dataframe as csv
    df.to_csv('data/predictions.csv', index = False)

    #upload csv to the output bucket
    upload_data('data/predictions.csv', output_bucket_name, input_file_name)

    #delete the tempfiles from data directory
    all_images = os.listdir('data/images')
    
    for file in all_images:
        os.remove(f"data/images/{file}")

    all_dicoms = os.listdir('data/dicom')

    for file in all_dicoms:
        os.remove(f"data/dicom/{file}")

    os.remove("input_zip.zip")
    os.remove("data/predictions.csv")

#create flask app
app = Flask(__name__)

@app.route("/", methods=["POST"])
def index():
    envelope = request.get_json()
    if not envelope:
        msg = "no Pub/Sub message received"
        print(f"error: {msg}")
        return f"Bad Request: {msg}", 400

    if not isinstance(envelope, dict) or "message" not in envelope:
        msg = "invalid Pub/Sub message format"
        print(f"error: {msg}")
        return f"Bad Request: {msg}", 400

    # Decode the Pub/Sub message.
    pubsub_message = envelope["message"]

    if isinstance(pubsub_message, dict) and "data" in pubsub_message:
        try:
            data = json.loads(base64.b64decode(pubsub_message["data"]).decode())

        except Exception as e:
            msg = (
                "Invalid Pub/Sub message: "
                "data property is not valid base64 encoded JSON"
            )
            print(f"error: {e}")
            return f"Bad Request: {msg}", 400

        # Validate the message is a Cloud Storage event.
        if not data["name"] or not data["bucket"]:
            msg = (
                "Invalid Cloud Storage notification: "
                "expected name and bucket properties"
            )
            print(f"error: {msg}")
            return f"Bad Request: {msg}", 400

        try:
            ## add function here
            run_inference(data)
            return ("", 204)

        except Exception as e:
            print(f"error: {e}")
            return ("", 500)

    return ("", 500)
