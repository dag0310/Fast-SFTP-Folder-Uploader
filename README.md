# Fast SFTP Folder Uploader

Upload folders faster via SFTP by temporarily zipping on the client and unzipping on the host.

## Features

- Very useful for folders with many files and folders, like a Wordpress instance.
- It also automatically deletes the temporary ZIP files locally and remotely.
- You can also just upload an existing ZIP file, which will not be deleted locally.
- If you just want to upload a ZIP file without remote extraction and deletion just use any other SFTP client.

## Development

Run: `python fast_sftp_folder_uploader.py`

Attention: Run in current working directory, otherwise the config will be saved to from where it was called.

### Windows

Tested with Windows 10:

- Install Python 3 from [python.org](https://www.python.org/)
- `pip install -r requirements.txt`
- Create executable
  - `pip install pyinstaller`
  - `pyinstaller --onefile fast_sftp_folder_uploader.py`

### Linux

Tested with Ubuntu 22:

- `sudo apt install python3`
- `sudo apt install python3-pip`
- `sudo apt install python3-tk`
- `pip install -r requirements.txt`
- Create executable
  - `pip install pyinstaller`
  - `~/.local/bin/pyinstaller --onefile fast_sftp_folder_uploader.py`