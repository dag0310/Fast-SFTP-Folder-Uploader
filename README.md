# Fast SFTP Folder Uploader

Uploads a folder fast to a set SFTP remote folder location by zipping it on the client, uploading the zip file and unzipping it on the remote host.

It also automatically deletes the temporary zip files locally and remotely.

Very useful for folders with many files and folders, like a Wordpress instance.

You can also just upload an existing ZIP file, which will not be deleted locally.

If you just want to upload a zip file without remote extraction use any other tool like FileZilla.

## Requirements

- Python 3
- Windows 10+
- Install dependencies: `pip install -r requirements.txt`
