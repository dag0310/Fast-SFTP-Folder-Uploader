# Fast SFTP Folder Uploader

Uploads a folder fast to a set SSH remote folder location by zipping it on the client, uploading the zip file and unzipping it on the remote host.

It also automatically deletes the temporary zip files locally and remotely.

Very useful for folders with many files and folders, like a Wordpress instance.

If you just want to upload a zip file use any other tool like FileZilla.

## Requirements

- Python 3
- Windows 10+
- Install dependencies: `pip install -r requirements.txt`
