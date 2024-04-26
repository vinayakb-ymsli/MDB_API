from flask import Flask,request,jsonify
import os
from dotenv import load_dotenv
import boto3
import io
from uuid import uuid4  # For generating unique filenames
import requests
import time
from flask_cors import CORS
import base64
from utils import fetch_files_from_zip_variable
from pathlib import Path
from pathlib import Path



from zipfile import ZipFile 

load_dotenv()

app = Flask(__name__)
CORS(app)

ACCESS_KEY=os.getenv('ACCESS_KEY')
SECRET_KEY=os.getenv('SECRET_KEY')
BUCKET_NAME=os.getenv('BUCKET_NAME')
CLOUDFRONT_URL=os.getenv('CLOUDFRONT_URL')
FOLDER_NAME=os.getenv('FOLDER_NAME')

# @app.route('/', methods=['GET'])
# def home():
#     return 'Hello World!!!'

# Function to upload image to S3 bucket
@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file uploaded'}), 400

    image_file = request.files['image']
    filename = f"{uuid4()}.{image_file.filename.split('.')[-1]}"

    filename_with_location = f"ValidationImages/{filename}"

    s3_client = boto3.client('s3', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)

    try:
        s3_client.upload_fileobj(image_file, BUCKET_NAME, filename_with_location)

        url = CLOUDFRONT_URL + FOLDER_NAME + '/processed_image_' + filename

        # Try to fetch the image 30 times
        for _ in range(30):
            try:
                response = requests.get(url, verify=False)
                response.raise_for_status()  # If the response contains an HTTP error status code, raise an exception
                base64_content = base64.b64encode(response.content).decode('utf-8')
                print(base64_content)
                return jsonify({'image': base64_content}), 200  # Return the image content
            except Exception as e:
                time.sleep(2)  # Wait for 2 seconds before the next attempt

        # If all attempts fail, return an error message
        return jsonify({'error': 'Not able to process file'}), 500
    except Exception as e:
        return jsonify({'error': f'Error uploading image: {str(e)}'}), 500


@app.route('/upload_zip', methods=['POST'])
def upload_zip():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    if file and file.filename.endswith('.zip'):

        uuid = str(uuid4())
        file_name = uuid + file.filename
        file_name = file_name.replace(" ", "_")
        file.save(os.path.join('temp_files',file_name))
        path = os.path.join('temp_files',file_name)
        saved_file_path = os.path.join('temp_files',uuid)

        with ZipFile(path, 'r') as zip: 
            # printing all the contents of the zip file 
            zip.printdir() 
            # extracting all the files 
            print('Extracting all the files now...') 
            zip.extractall(saved_file_path) 
            print('Done!') 


        return jsonify({'message': 'File uploaded successfully'})
    else:
        return jsonify({'error': 'Invalid file format. Please upload a .zip file'})
    



if __name__ == '__main__':
    Path("temp_files").mkdir(parents=True, exist_ok=True)
    app.run(debug=True,host='0.0.0.0',port=5000)

    # if 'zip' not in request.files:
    #     return jsonify({'error': 'No zip file uploaded'}), 400

    # zip_file = request.files['zip']
    # zip_data = zip_file.read()

    # file_contents = fetch_files_from_zip_variable(zip_data)

    # zip_data.printdir()

    # return jsonify(file_contents), 200