from zipfile import ZipFile
import io
import os
import requests
from flask import jsonify
import base64
import time

BUCKET_NAME = os.getenv('BUCKET_NAME')
CLOUDFRONT_URL = os.getenv('CLOUDFRONT_URL')
FOLDER_NAME=os.getenv('FOLDER_NAME')

def fetch_files_from_zip_variable(zip_data):
    # Create a file-like object from the zip data
    zip_file = io.BytesIO(zip_data)

    # Open the zip file
    with ZipFile(zip_file, 'r') as zip_ref:
        # Extract all files to a temporary directory
        temp_dir = 'temp_dir'
        zip_ref.extractall(temp_dir)

        # Get the list of files
        files = os.listdir(temp_dir)

        # Read the content of each file
        file_contents = {}
        for file in files:
            with open(os.path.join(temp_dir, file), 'r') as f:
                file_contents[file] = f.read()

    return file_contents

def save_input_file_into_bucket(s3_client, image_file, filename):
        filename_with_s3_location = f"ValidationImages/{filename}"

        s3_client.upload_fileobj(image_file, BUCKET_NAME, filename_with_s3_location)

# returns file in base64 format
def fetch_output_file_from_bucket(filename):
    url = CLOUDFRONT_URL + FOLDER_NAME + '/processed_image_' + filename

    # Try to fetch the image 30 times
    for _ in range(30):
        try:
            response = requests.get(url, verify=False)
            response.raise_for_status()  # If the response contains an HTTP error status code, raise an exception
            base64_content = base64.b64encode(response.content).decode('utf-8')
            print(base64_content)
            return base64_content
        except:
            time.sleep(2)  # Wait for 2 seconds before the next attempt
    raise Exception()
