

# iManualTransfer

## Introduction

iManualTransfer is crafted to automatically transfer photos and videos from an iPhone to a Mac. In some situations like my phone that was crashing randomly every two or three minute, you can't use tools like iDeviceBackup2 or iTunes to recover your pictures given those programs like all the others, can't cope with the fact that the phone will disconnect any number of times during the backup, stopping the backup process. By utilizing `libimobiledevice` and `ifuse`, those scripts offer a streamlined alternative to traditional media transfer methods. The process is resilient to crashes or phone disconnection.

## Project Goals

- **Direct Transfer**: Facilitate the direct transfer of media from an iPhone to a Mac, ensuring efficiency and ease.
- **Automation**: Use a Python script to automate detection and transfer processes, reducing manual efforts.
- **Reliability**: Implement robust logic to manage devices that frequently disconnect or crash, providing a dependable transfer solution.

## Setup Instructions

### Prerequisites

- A Mac running macOS (10.14 Mojave or later recommended).
- An iPhone, ideally with a USB cable for initial setup.

### Step 1: Install Homebrew

Homebrew simplifies software installation on macOS. Open Terminal and run:

```sh
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Step 2: Install `libimobiledevice`

After installing Homebrew, install `libimobiledevice`:

```sh
brew install libimobiledevice
```

### Step 3: Install `ifuse`

`ifuse` allows for mounting and unmounting of your iOS device's filesystem. Follow these steps to install `ifuse` and its dependencies:

1. **Uninstall `osxfuse` if it's already installed**:

   ```sh
   brew uninstall osxfuse
   ```

2. **Install `macfuse`**:

   ```sh
   brew install --cask macfuse
   ```

3. **Install `ifuse`**:

   ```sh
   brew install gromgit/fuse/ifuse-mac # version 1.1.4
   ```

   Thanks to Chuck Batson for the instructions. Visit [cbatson/how-to-install-ifuse-on-macos.md](https://github.com/gromgit/homebrew-fuse) for more details.

4. **Restart your Mac** to ensure `ifuse` is correctly added to your PATH.

5. **Enable kernel extension** if required by following instructions at [https://github.com/macfuse/macfuse/wiki/Getting-Started](https://github.com/macfuse/macfuse/wiki/Getting-Started).

6. **Troubleshoot `ifuse` library errors**:

   If you encounter an error like the one below when running `ifuse`:

   ```sh
   dyld[1352]: Library not loaded: /opt/homebrew/opt/libplist/lib/libplist-2.0.3.dylib
     Referenced from: /opt/homebrew/Cellar/ifuse-mac/1.1.4/bin/ifuse
   ```

   Try linking the correct `libplist` version:

   ```sh
   ( cd "$(brew --prefix)/opt/libplist/lib/" && ln -s libplist-2.0.4.dylib libplist-2.0.3.dylib )
   ```

   For details, see [this guide](https://github.com/asbjornu).

7. **Resolve 'Operation not permitted' errors**:

   If you encounter this error after mounting, grant Terminal access to "Network Volumes" in system settings.

### Step 4: Install Python

Install Python 3 using Homebrew:

```sh
brew install python
```

### Step 5: Verify Python Installation

Ensure Python 3 is correctly installed:

```sh
python3 --version
```

### Step 6: Prepare the Python Script

Place your Python script in a convenient directory on your Mac. It should utilize `libimobiledevice` and `ifuse` for device communication.

### Step 7: Run the Python Script

Navigate to your script's directory in Terminal and execute it. You obviously need write access in your current location:

```sh
python3 list/retrieve/shrink.py
```

## Troubleshooting

- **Device Not Recognized**: Verify the iPhone is unlocked and trust the Mac. Reconnect the USB cable and restart both devices if necessary.
- **`libimobiledevice` and `ifuse` Errors**: Ensure the latest versions are used. Update with `brew update`, `brew upgrade libimobiledevice`, and follow the `ifuse` troubleshooting steps.
- **Python Errors**: Check all dependencies and script compatibility with the Python version in use.
- **Error mounting device**: sometimes ifuse will not be able to remount the device for some reason.
```sh
2024-02-23 21:32:07 - Error mounting device: Command '['ifuse', '/Users/jonx/Desktop/Repos/jonx/temp/Session_20240223_213207']' returned non-zero exit status 1.
2024-02-23 21:32:07 - Failed to mount device. Retrying...
```
Sometimes killing the script using CTRL+C and restart will be enough but most of the time you'll need to restart your computer. Sorry for the inconvenience.

# Running iManualTransfer

Notes that the script will be more or less slow depending how often your device is crashing but those scripts are here for the long run and won't mind too much. Transfering 25K files from an iPhone SE 1st Gen that was crashing every two or three minutes took about 24 hours but I guess you won't mind too much if that's the only way to get your files back.

## Setup

Before using iManualTransfer, ensure you have installed the necessary dependencies for interfacing with an iPhone's filesystem on a Mac. This includes tools like `libimobiledevice` `ifuse` or `usbmuxd` for mounting and accessing the iPhone's filesystem and others required for the scripts to function correctly.

## Script Descriptions

### 1. `list`

The `list` script is designed to generate a comprehensive list of files available for transfer from the iPhone. This is the first step in the transfer process, providing a clear overview of the files you can choose to transfer.

- **Purpose**: To identify and catalog all files on the iPhone that are available for transfer.
- **Usage**: Run this script to output a list of files into `files_to_copy.json`. You can then review this list to decide which files you wish to transfer.
- **Note**: Your files will be tranfered to where you're running the script from. So your media should be copied directly in a `DCIM` sub-folder but in case you copy everything you can access on the phone, it might get messy quickly. The script is easy to modify to put everything in a subfolder instead.

### 2. `retrieve`

The `retrieve` script does the actual transfer of files from the iPhone to the Mac. It will tranfer the files listed in `files_to_copy.json`. This files contains the name and the size of the file that is used to ensure the transfer was completed. The script will recreate directories, especially given the pictures on an iDevice can have colliding names.

- **Purpose**: To copy selected files from the iPhone to the Mac, ensuring they are transferred accurately and intact.
- **Usage**: The script will copy the file, verifying its integrity post-transfer. There is a check in the script that let's you focus on files of a given size (`if file_info['size'] > 60000000:`). I started small with less then 1 MB and went up gradualy. Again, given the phone is crashing, you're going to have a hard time if there is a bigger file that can't be copied fast enough between two crashes. 
- **Note**: The script will mount the phone to a new folder in the temp folder every time it reconnects because sometimes, the mounted folder gets stuck and can't be used or even removed anymore. Once you are done, just remove the temp directory. If you can't because some files are still locked, you might have to eject the mounbted folder from the computer. Worst case, just restart your computer and you'll be able to remove the temp director.

### 3. `shrink`

After successfully transferring files, the `shrink` script helps update the list by removing the entries of transferred files. This keeps the transfer list lean and makes sure you're not losing too much time testing for successful file transfers before copying your remaining files. Depending on how often the phone crashes, you should run the script regularly. All it does is removing the files already copied from the list.

- **Purpose**: To maintain a lean list of files pending transfer by removing those already transferred.
- **Usage**: The script updates the list in `files_to_copy.json`, excluding the completed transfer.
- **Note**: I suggest you keep a copy of the initial `files_to_copy.json` that has all the filenames so that you can run it against the full list once your done to ensure you haven't missed anything.

## Workflow Efficiency

- **File Integrity Verification**: Each transfer is verified to ensure files are copied correctly, maintaining the integrity of your data.
- **Process Resumption**: Initially, an attempt was made to implement a feature for resuming transfers based on the last processed file, including restarting the listing process if needed. This was aimed at enhancing efficiency, especially in scenarios requiring transfer interruption or system restarts. While this feature was not fully implemented, the current workflow is designed to be straightforward and manageable, with potential for future enhancements.
- **Chunk copy**: If the files you want to copy are too big to be copied between two crashes, you would need to modify the script and implement a copy in chunk method that will restart copying the file when it left the last time it crashed.

## Conclusion

iManualTransfer provides a robust approach for transferring files from an iPhone to a Mac. Through its three-script system are not the most easy or even fastest process to transfer files from an iDevice but in my case, it was the only way given all the other tools I know can't cope with a crashing device. I hope it helps.
