import tkinter as tk
from tkinter import StringVar, filedialog
import paramiko
import os
import platform
import configparser

# Create or read the configuration file
config = configparser.ConfigParser()
config_file = 'config.ini'

if os.path.exists(config_file):
    config.read(config_file)


def update_status(text):
    print(text)
    output_text.set(text)


def zip_and_upload(local_folderpath, remote_folderpath, hostname, username, password):
    zip_filename = None
    try:
        if local_folderpath == '':
            raise Exception("Please select a folder.")

        # Create a temporary zip file
        update_status('[LOCAL] Preparing folder for upload ...')
        cwd = os.getcwd()
        folder_name = os.path.basename(local_folderpath)
        zip_filename = folder_name + ".zip"
        os.chdir(local_folderpath)
        os.chdir('..')
        zip_command = 'tar -a -c -f "' + os.path.join(cwd, zip_filename) + '" "' + folder_name + '"'
        print('[LOCAL] ' + zip_command)
        os.system(zip_command)
        os.chdir(cwd)

        # Create an SSH client
        update_status('[LOCAL] Establishing connection to remote ...')
        ssh_client = paramiko.SSHClient()
        ssh_client.load_system_host_keys()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect to the remote host
        ssh_client.connect(hostname, username=username, password=password)

        # Create an SFTP client
        sftp = ssh_client.open_sftp()

        # Upload the zip file to the remote folder
        update_status('[LOCAL] Uploading to remote ...')
        if remote_folderpath == '':
            remote_filepath = zip_filename
        elif remote_folderpath[-1] == '/':
            remote_filepath = remote_folderpath + zip_filename
        else:
            remote_filepath = remote_folderpath + "/" + zip_filename

        print("[LOCAL] sftp.put('" + zip_filename + "', '" + remote_filepath + "')")
        sftp.put(zip_filename, remote_filepath)

        # Execute the unzip command remotely
        update_status('[REMOTE] Saving folder ...')
        remote_unzip_command = 'unzip ' + remote_filepath + ' -d ' + remote_folderpath
        ssh_client.exec_command(remote_unzip_command)
        print('[REMOTE] ' + remote_unzip_command)
        remote_rm_command = 'rm ' + remote_filepath
        ssh_client.exec_command(remote_rm_command)
        print('[REMOTE] ' + remote_rm_command)

        # Close the SFTP session and SSH connection
        sftp.close()
        ssh_client.close()

        update_status('[REMOTE] Folder uploaded successfully!')
    except Exception as e:
        update_status(str(e))
    finally:
        # Remove the temporary zip file
        if zip_filename is not None and os.path.exists(zip_filename):
            os.remove(zip_filename)
            print("[LOCAL] Temporary local zip file removed.")


def browse_folder():
    local_folder = filedialog.askdirectory()
    local_folder_entry.delete(0, tk.END)
    local_folder_entry.insert(0, local_folder)
    update_status('Folder selected.')


def upload():
    local_folder = local_folder_entry.get()
    remote_folder = remote_folder_entry.get()
    hostname = hostname_entry.get()
    username = username_entry.get()
    password = password_entry.get()

    zip_and_upload(local_folder, remote_folder, hostname, username, password)


def save_config():
    config['SFTP']['remote_folder'] = remote_folder_entry.get()
    config['SFTP']['hostname'] = hostname_entry.get()
    config['SFTP']['username'] = username_entry.get()
    config['SFTP']['password'] = password_entry.get()

    with open(config_file, 'w') as configfile:
        config.write(configfile)
    update_status('Config saved.')


# Create the main window
root = tk.Tk()
root.title("Fast SFTP Folder Uploader")

# Local folder selection
local_folder_label = tk.Label(root, text="Local Folder:")
local_folder_label.pack()
local_folder_entry = tk.Entry(root)
local_folder_entry.pack()
browse_button = tk.Button(root, text="Browse", command=browse_folder)
browse_button.pack()

# Remote folder and SFTP settings
remote_folder_label = tk.Label(root, text="Remote Folder:")
remote_folder_label.pack()
remote_folder_entry = tk.Entry(root)
remote_folder_entry.pack()

hostname_label = tk.Label(root, text="SFTP Hostname:")
hostname_label.pack()
hostname_entry = tk.Entry(root)
hostname_entry.pack()

username_label = tk.Label(root, text="Username:")
username_label.pack()
username_entry = tk.Entry(root)
username_entry.pack()

password_label = tk.Label(root, text="Password:")
password_label.pack()
password_entry = tk.Entry(root, show="*")
password_entry.pack()

# Load saved configuration
remote_folder_entry.insert(0, config['SFTP']['remote_folder'])
hostname_entry.insert(0, config['SFTP']['hostname'])
username_entry.insert(0, config['SFTP']['username'])
password_entry.insert(0, config['SFTP']['password'])

# Save button
save_button = tk.Button(root, text="Save Config", command=save_config)
save_button.pack()

# Upload button
upload_button = tk.Button(root, text="Upload folder", command=upload)
upload_button.pack()

output_text = StringVar()
output_text.set('Select a local folder to upload.')
output_label = tk.Label(root, textvariable=output_text)
output_label.pack()

root.mainloop()
