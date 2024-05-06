from flask import Flask,request,jsonify
import os
from dotenv import load_dotenv
import boto3
from uuid import uuid4

from flask_cors import CORS
import base64
from utils import fetch_files_from_zip_variable, save_input_file_into_bucket, fetch_output_file_from_bucket
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


image_details = {
    'image_dimensions': '1024 x 772',
    'model_name': 'm1',
    'model_upload_date': '2024-05-06',
    'model_type': 'stardist'
}


# Function to upload image to S3 bucket
@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file uploaded'}), 400

    image_file = request.files['image']
    filename = f"{uuid4()}.{image_file.filename.split('.')[-1]}"

    try:
        save_input_file_into_bucket(s3_client, image_file, filename)
        base64_output_image = fetch_output_file_from_bucket(filename)

        return jsonify({'image': base64_output_image})
    except Exception as e:
        return jsonify({'error': 'Error uploading image'}), 500
    


@app.route('/upload_zip', methods=['POST'])
def upload_zip():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    if file and file.filename.endswith('.zip'):
        uuid = str(uuid4())
        file_name = file.filename #secure_filename(file.filename)
        saved_file_path = os.path.join('temp_files',uuid)

        if not os.path.exists(saved_file_path):
            os.makedirs(saved_file_path)

        zipfile_path = os.path.join(saved_file_path,file_name)
        file.save(zipfile_path)
        # path = os.path.join(saved_file_path,file_name.split('.')[0])


        with ZipFile(zipfile_path, 'r') as zip: 
            zip.extractall(saved_file_path) 

        input_images_path = os.path.join(saved_file_path, file_name.split('.')[0])

        processed_images = {}
        original_images = {}

        for filename in os.listdir(input_images_path):
            file_path = os.path.join(input_images_path, filename)
            with open(file_path, 'rb') as f:
                filename_for_s3 = uuid + filename
                save_input_file_into_bucket(s3_client, f, filename_for_s3)
            processed_image_base64 = fetch_output_file_from_bucket(filename_for_s3)
            # processed_image_with_filename = {filename.split('.')[0]: processed_image_base64}
            # processed_images.append(processed_image_with_filename)
            processed_images[filename.split('.')[0]] = processed_image_base64
            original_images[filename.split('.')[0]] = base64.b64encode(open(os.path.join(input_images_path, filename), 'rb').read()).decode('utf-8')
        return jsonify({'processed_images': processed_images, 'original_images': original_images, 'image_details': image_details})
    else:
        return jsonify({'error': 'Invalid file format. Please upload a .zip file'})



if __name__ == '__main__':
    Path("temp_files").mkdir(parents=True, exist_ok=True)
    s3_client = boto3.client('s3', aws_access_key_id=ACCESS_KEY, aws_secret_access_key=SECRET_KEY)
    app.run(debug=True,host='0.0.0.0',port=5000)
