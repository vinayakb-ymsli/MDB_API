from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponse
import os
import boto3
import io
from uuid import uuid4 # For generating unique filenames
from django.conf import settings
from botocore.exceptions import NoCredentialsError, PartialCredentialsError
import json

@api_view(['GET'])
def test(requests):
    # print(settings.ACCESS_KEY)
    return HttpResponse("working")

@api_view(['GET'])
def folder_contents(requests):
    data = requests.data
    s3 = boto3.client('s3', aws_access_key_id=settings.ACCESS_KEY, aws_secret_access_key=settings.KEY_AWS, region_name=settings.REGION_NAME)
    folder_contents = get_s3_folder_contents_as_string(s3, settings.BUCKET_NAME, data['folder_name'])
    return Response(folder_contents)


@api_view(['POST'])
def create_client(requests):
    data = (requests.data)
    folder_name = data['client_name']
    bucket_name = settings.BUCKET_NAME

    # Initialize a session using Amazon S3
    s3 = boto3.client('s3', aws_access_key_id=settings.ACCESS_KEY, aws_secret_access_key=settings.KEY_AWS, region_name=settings.REGION_NAME)
    # The key for a "folder" ends with a '/'
    folder_key = f'{folder_name}/'
    try:
        # Create the folder by putting a zero-byte object with a folder key
        s3.put_object(Bucket=bucket_name,Body='', Key=folder_key)
        print(f'Folder "{folder_name}" created successfully in bucket "{bucket_name}".')
        return Response ("{'success 200':'client created succesfully'}")
    
    except NoCredentialsError:
        print('Credentials not available.')
        return Response ("{'error 500':'Credentials not available.'}")
    
    except PartialCredentialsError:
        print('Incomplete credentials provided.')
        return Response ("{'error 500':'Credentials not available.'}")
    
@api_view(['POST'])
def create_project(requests):
    data = (requests.data)
    folder_name = data['client_name']
    project_name = data['project_name']
    bucket_name = settings.BUCKET_NAME

    # Initialize a session using Amazon S3
    s3 = boto3.client('s3', aws_access_key_id=settings.ACCESS_KEY, aws_secret_access_key=settings.KEY_AWS, region_name=settings.REGION_NAME)
    # The key for a "folder" ends with a '/'
    folder_key = f'{folder_name}/{project_name}/'
    try:
        # Create the folder by putting a zero-byte object with a folder key
        s3.put_object(Bucket=bucket_name,Body='', Key=folder_key)
        print(f'Project "{project_name}" created successfully in bucket "{bucket_name}".')
        return Response ("{'success 200':'Project created succesfully'}")
    
    except NoCredentialsError:
        print('Credentials not available.')
        return Response ("{'error 500':'Credentials not available.'}")
    
    except PartialCredentialsError:
        print('Incomplete credentials provided.')
        return Response ("{'error 500':'Credentials not available.'}")
    
@api_view(['POST'])
def create_model(requests):
    data = (requests.data)
    folder_name = data['client_name']
    project_name = data['project_name']
    model_name = data['model_name']
    bucket_name = settings.BUCKET_NAME

    # Initialize a session using Amazon S3
    s3 = boto3.client('s3', aws_access_key_id=settings.ACCESS_KEY, aws_secret_access_key=settings.KEY_AWS, region_name=settings.REGION_NAME)
    # The key for a "folder" ends with a '/'
    folder_key = f'{folder_name}/{project_name}/{model_name}'
    try:
        # Create the folder by putting a zero-byte object with a folder key
        s3.put_object(Bucket=bucket_name,Body='', Key=folder_key)
        print(f'Model "{model_name}" created successfully in bucket "{bucket_name}".')
        return Response ("{'success 200':'Model created succesfully'}")
    
    except NoCredentialsError:
        print('Credentials not available.')
        return Response ("{'error 500':'Credentials not available.'}")
    
    except PartialCredentialsError:
        print('Incomplete credentials provided.')
        return Response ("{'error 500':'Credentials not available.'}")
    
def get_s3_folder_contents_as_string(s3_client, bucket_name, folder_name):
    try:
        # List objects within the specified folder
        response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=folder_name)
        
        if 'Contents' not in response:
            print(f"No contents found in folder '{folder_name}'")
            return ""

        # Initialize an empty string to accumulate the contents
        folder_contents = ""

        # Iterate through each object in the folder
        for obj in response['Contents']:
            key = obj['Key']
            
            print(f"Reading object: {key}")

            # # Get the object
            # obj_response = s3_client.get_object(Bucket=bucket_name, Key=key)

            # # Read the object content and decode it to a string
            # content = obj_response['Body'].read().decode('utf-8')
            # folder_contents += key + "\n"
        folder_contents=key

        return folder_contents
    except Exception as e:
        print("Unexpected error:", e)
    return ""