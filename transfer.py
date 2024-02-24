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
import subprocess
import json
import time
import shutil
from datetime import datetime

# Base path for script operation
base_path = os.getcwd()
temp_directory = os.path.join(base_path, "temp")
log_file = os.path.join(base_path, "iphone_log.txt")
state_file = os.path.join(base_path, "iphone_state.json")
files_to_copy_file = os.path.join(base_path, "files_to_copy.json")
destination_root = base_path # Add somthing here if you don't want your files to be copied `here`.

if not os.path.exists(temp_directory):
    os.makedirs(temp_directory)

def log_message(message):
    with open(log_file, 'a') as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        full_message = f"{timestamp} - {message}\n"
        print(full_message, end='')
        f.write(full_message)

def save_state(state):
    with open(state_file, 'w') as f:
        json.dump(state, f)

def load_state():
    if os.path.exists(state_file):
        with open(state_file) as f:
            return json.load(f)
    return {"last_attempted_file": "", "processed_files": 0}

# Update this function to also save 'last_attempted_file'
def update_last_attempted_file(file_path):
    state = load_state()
    state['last_attempted_file'] = file_path
    save_state(state)

def create_session_directory():
    session_folder_name = datetime.now().strftime("Session_%Y%m%d_%H%M%S")
    session_directory = os.path.join(temp_directory, session_folder_name)
    os.makedirs(session_directory, exist_ok=True)
    return session_directory

def mount_device(device_directory):
    try:
        subprocess.run(["ifuse", device_directory], check=True)
        log_message(f"Device mounted to: {device_directory}") 
        return True
    except subprocess.CalledProcessError as e:
        log_message(f"Error mounting device: {e}")
        return False

def unmount_device(device_directory):
    # Adjust this command for your setup; this uses diskutil for macOS
    try:
        subprocess.run(["diskutil", "unmount", device_directory], check=True)
        log_message(f"Unmount successful for {device_directory}")
    except subprocess.CalledProcessError:
        log_message("Error unmounting device.")

def is_device_connected():
    result = subprocess.run(["idevice_id", "-l"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True)
    return result.stdout.strip() != ""

def is_filesystem_mounted(device_directory):
    try:
        if os.listdir(device_directory):  # Attempt to list the contents
            return True
    except OSError:
        return False
    return False

def read_files_to_copy(files_to_copy_path):
    with open(files_to_copy_path, 'r') as file:
        files_to_copy = [json.loads(line) for line in file]
    
    # Sort the files by size from biggest to smallest
    files_to_copy.sort(key=lambda x: x['size']) #, reverse=True)
    
    for file_info in files_to_copy:
        yield file_info

def copy_file(source_path, destination_path):
    # Ensure the destination directory exists
    os.makedirs(os.path.dirname(destination_path), exist_ok=True)
    # Copy the file
    shutil.copy2(source_path, destination_path)

# def verify_file_size(source_path, destination_path):
#     return os.path.getsize(source_path) == os.path.getsize(destination_path)

def verify_file_size(source_path, destination_path):
    try:
        return os.path.getsize(source_path) == os.path.getsize(destination_path)
    except OSError as e:
        log_message(f"Error verifying file size: {e}. Skipping file.")
        return False  # Consider the file as not verified to safely handle the error

def retrieve_files(session_path):
    if not is_filesystem_mounted(session_path):
        log_message("Filesystem not mounted or accessible.")
        return False  # Filesystem not accessible

    # state = load_state()
    # last_attempted_file = state.get('last_attempted_file', "")
    # found_last_attempted = False if last_attempted_file else True

    # if last_attempted_file:
    #     log_message(f"Last attempted file: {last_attempted_file}. Looking for this file to restart.")

    for file_info in read_files_to_copy(files_to_copy_file):
        source_path = os.path.join(session_path, file_info['path'])
        destination_path = os.path.join(destination_root, file_info['path'])

        # # If we have a last attempted file and haven't found it yet, check if this is the file
        # if not found_last_attempted:
        #     if source_path == last_attempted_file:
        #         found_last_attempted = True
        #         log_message(f"Found last attempted file: {last_attempted_file}. Restarting from here.")
        #     else:
        #         continue  # Skip files until we find the last attempted one

        # Check file size limit
        # if file_info['size'] > 60000000:
        #     log_message(f"File exceeds size limit (60,000,000 bytes), skipping: {file_info['path']}")
        #     continue  # Skip to the next file

        # Check if destination file exists and has the correct size
        if os.path.exists(destination_path) and verify_file_size(source_path, destination_path):
            log_message(f"File already exists with correct size, skipping: {file_info['path']}")
            continue  # Skip to the next file

        # Attempt to skip existing files with correct size, handling potential I/O errors
        try:
            if os.path.exists(destination_path) and verify_file_size(source_path, destination_path):
                log_message(f"File already exists with correct size, skipping: {file_info['path']}")
                # file_info['copied'] = True  # Mark as copied to skip in future iterations
                continue
        except OSError as e:
            log_message(f"Error verifying size for {file_info['path']}: {e}. Skipping.")

        try:
            copy_file(source_path, destination_path)
            if verify_file_size(source_path, destination_path):
                log_message(f"Successfully copied: {file_info['path']}")
            else:
                log_message(f"File size mismatch, retrying: {file_info['path']}")
                # Handle size mismatch (optional: retry copy or log error)
        except Exception as e:
            log_message(f"Error copying file {file_info['path']}: {e}.")
            return False  # Return False to indicate an error occurred and to potentially restart from the last attempted file

    return True  # Return True when all files are processed without encountering an error

def main_loop():

    try:
        while True:
            if is_device_connected():
                # Each time device is connected, create a new session directory in temp
                session_directory = create_session_directory()
                log_message(f"Device connected...")
                if mount_device(session_directory):
                    completed = retrieve_files(session_directory)
                    if completed:
                        log_message("All files processed. Exiting...")
                        break  # Exit the loop and end the script
                    else:
                        log_message("Session completed. There might be more files to process in the next session.")
                else:
                    log_message("Failed to mount device. Retrying...")
            else:
                log_message("Device disconnected. Waiting...")
                time.sleep(5)  # Wait before retrying

    except KeyboardInterrupt:
        # When Ctrl+C is pressed, KeyboardInterrupt is caught here
        log_message("Ctrl+C pressed. Saving progress and exiting...")

if __name__ == "__main__":
    main_loop()
