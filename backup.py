#!/usr/bin/python3
import os
import zipfile
import argparse

def create_zip_with_password(directories_to_zip, zip_filename):
    # Set the path for the zip file
    zip_filepath = f"/TopStordata/{zip_filename}.zip"
    
    # Create a ZipFile object without password (initially)
    with zipfile.ZipFile(zip_filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for directory in directories_to_zip:
            if os.path.exists(directory):
                for root, dirs, files in os.walk(directory):
                    for file in files:
                        file_path = os.path.join(root, file)
                        # Add each file to the zip file with relative path
                        zipf.write(file_path, os.path.relpath(file_path, directory))
            else:
                print(f"Warning: Directory {directory} does not exist.")
    
    # Set the password using the system's zip utility with encryption (-e flag)
    os.system(f"zip -e -P {zip_filename} {zip_filepath} > /dev/null 2>&1")


    if os.path.exists(zip_filepath):
        print(f"Zip file {zip_filename}.zip created with password protection")
    else:
        print(f"Error: Failed to create {zip_filename}.zip")


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Create a password-protected zip file.")
    parser.add_argument('filename', help="The name of the zip file (also used as the password)")
    args = parser.parse_args()

    # Define the three directories to be zipped
    directories = ['/TopStor', '/topstorweb', '/pace']
    
    # Call the zip function
    create_zip_with_password(directories, args.filename)

if __name__ == "__main__":
    main()
