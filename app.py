from flask import Flask,request,jsonify
import os
from dotenv import load_dotenv
import boto3
import io
from uuid import uuid4  # For generating unique filenames

load_dotenv()

app = Flask(__name__)

ACCESS_KEY=os.getenv('ACCESS_KEY')
SECRET_KEY=os.getenv('SECRET_KEY')
BUCKET_NAME=os.getenv('BUCKET_NAME')

@app.route('/', methods=['GET'])
def home():
    return 'Hello World!!!'

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

        cdn = 'https://d1z61jdqkglv9s.cloudfront.net'
        url = cdn + '/OutputImages' + '/processed_image_' + filename

        return jsonify({'url': url}), 200
    except Exception as e:
        return jsonify({'error': f'Error uploading image: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=5001)

