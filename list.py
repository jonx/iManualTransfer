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
from datetime import datetime

# Base path for script operation
base_path = os.getcwd()
temp_directory = os.path.join(base_path, "temp")
log_file = os.path.join(base_path, "iphone_log.txt")
state_file = os.path.join(base_path, "iphone_state.json")
files_to_copy_file = os.path.join(base_path, "files_to_copy.json")

# Ensure temp_directory exists
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
    return {"last_file": "", "processed_files": 0, "last_path": ""}

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

def list_files(session_path, last_file="", processed_files=0, last_path=""):
    if not is_filesystem_mounted(session_path):
        log_message("Filesystem not mounted or accessible.")
        return False  # Filesystem not accessible

    log_message(f"We're trying to list this folder: {session_path}")
    completed_processing = True  # Assume completion unless proven otherwise
    resumed = False  # Flag to indicate if we have resumed from a saved state

    with open(files_to_copy_file, 'a') as f:  # Open the file in append mode
        for root, dirs, files in os.walk(session_path):
            dirs.sort()
            files.sort()

            # Check if we are at or beyond the last processed path
            if not resumed:
                if root < last_path:
                    continue  # Skip this directory
                elif root == last_path:
                    resumed = True  # We are resuming from the last processed directory
                    if last_file in files:
                        files = files[files.index(last_file) + 1:]  # Skip processed files
                else:
                    resumed = True  # We are past the last processed directory

            # Process files in the current directory
            for name in files:
                file_path = os.path.join(root, name)
                relative_path = os.path.relpath(file_path, session_path)  # Get relative path
                size = os.path.getsize(file_path)
                file_info = {"path": relative_path, "size": size}
                f.write(json.dumps(file_info) + "\n")  # Write file info as JSON line
                log_message(f"Processing file: {file_path}")
                processed_files += 1
                save_state({"last_file": name, "processed_files": processed_files, "last_path": root})

            if not files:
                log_message(f"Done listing files from directory: {root}")
    return completed_processing

def main_loop():
    # Initialize state with a default value if applicable
    #state = {"path": None, "last_file": None, "processed_files": 0}

    try:
        while True:
            if is_device_connected():
                # Each time device is connected, create a new session directory in temp
                session_directory = create_session_directory()
                log_message(f"Device connected...")
                if mount_device(session_directory):
                    state = load_state()
                    completed = list_files(session_directory, state["last_file"], state["processed_files"], state["last_path"])
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
