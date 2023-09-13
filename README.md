# Fast SFTP Folder Uploader

Upload folders faster via SFTP by temporarily zipping on the client and unzipping on the host.

## Features

- Very useful for folders with many files and folders, like a Wordpress instance.
- It also automatically deletes the temporary ZIP files locally and remotely.
- You can also just upload an existing ZIP file, which will not be deleted locally.
- If you just want to upload a ZIP file without remote extraction and deletion just use any other SFTP client.

## Requirements

- Python 3
- Windows 10+
- Install dependencies: `pip install -r requirements.txt`
