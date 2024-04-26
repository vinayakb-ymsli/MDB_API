from zipfile import ZipFile
import io
import os

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
