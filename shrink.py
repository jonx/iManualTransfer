#
# iManualTransfer Toolkit (https://github.com/jonx/iManualTransfer)
# Author: John Knipper

# Description:
# This toolkit facilitates manual file transfers from an iPhone to a Mac. It consists of three main scripts: `list`, `retrieve`, and `shrink`. Each script plays a vital role in ensuring efficient, user-driven file management between devices.

# Disclaimer:
# This code is provided "as is", without warranty of any kind, express or implied. The author is not responsible for any damages that may arise from the use of this code.

# License:
# This work is made available by John Knipper under the terms that it can be freely used, modified, and shared by anyone for any purpose without any restrictions or licensing requirements.
# 

import os
import json
from datetime import datetime

base_path = os.getcwd()
files_to_copy_file = os.path.join(base_path, "files_to_copy.json")
destination_root = base_path # "DCIM" is in the filename already

def log_message(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_message = f"{timestamp} - {message}"
    print(full_message)

def verify_file_size(source_size, destination_path):
    """Verify if the destination file exists and has the correct size."""
    try:
        return os.path.getsize(destination_path) == source_size
    except OSError as e:
        log_message(f"Error verifying file size for {destination_path}: {e}. Skipping file.")
        return False

def update_files_to_copy():
    """Update the JSON file to remove entries of files already copied."""
    updated_files_to_copy = []
    
    with open(files_to_copy_file, 'r') as file:
        for line in file:
            try:
                file_info = json.loads(line)
                destination_path = os.path.join(destination_root, file_info['path'])

                # If the file does not exist at the destination or size is incorrect, keep it in the list
                if not (os.path.exists(destination_path) and verify_file_size(file_info['size'], destination_path)):
                    updated_files_to_copy.append(file_info)
            except json.JSONDecodeError as e:
                log_message(f"Error decoding JSON from line: {e}. Skipping line.")
    
    # Rewrite the JSON file with the updated list
    with open(files_to_copy_file, 'w') as file:
        for file_info in updated_files_to_copy:
            file.write(json.dumps(file_info) + '\n')  # Write each JSON object on a new line

    log_message(f"Updated files_to_copy.json. Remaining files to copy: {len(updated_files_to_copy)}")

if __name__ == "__main__":
    update_files_to_copy()
