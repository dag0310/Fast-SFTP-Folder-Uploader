import tkinter as tk
from tkinter import StringVar, filedialog
import paramiko
import os
import configparser
import platform

config_filepath = 'config.ini'
zip_file_extension = '.zip'


def update_status(text):
    print(text)
    output_text.set(text)


def zip_and_upload(local_path, remote_folderpath, hostname, username, password):
    zip_filepath = None
    is_temporary_zip_file = False
    try:
        if local_path == '':
            raise Exception("Please select a folder or ZIP file.")

        basename = os.path.basename(local_path)
        if basename.endswith(zip_file_extension):
            print('Using selected ZIP file.')
            is_temporary_zip_file = False
            zip_filename = basename
            zip_filepath = local_path
        else:
            print('Creating temporary ZIP file ...')
            is_temporary_zip_file = True
            cwd = os.getcwd()
            folder_name = os.path.basename(local_path)
            zip_filename = folder_name + zip_file_extension
            zip_filepath = os.path.join(cwd, zip_filename)
            os.chdir(local_path)
            os.chdir('..')
            if platform.system() == 'Windows':
                zip_command = 'tar -a -c -f "' + zip_filepath + '" "' + folder_name + '"'
            else:
                zip_command = 'zip -r "' + zip_filepath + '" "' + folder_name + '"'
            print(zip_command)
            os.system(zip_command)
            os.chdir(cwd)

        print('Creating SSH client ...')
        ssh_client = paramiko.SSHClient()
        ssh_client.load_system_host_keys()
        ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        print('Connecting to remote host ...')
        ssh_client.connect(hostname, username=username, password=password)

        print('Creating SFTP client ...')
        sftp = ssh_client.open_sftp()

        print('Uploading ZIP file to remote folder ...')
        if remote_folderpath == '' or remote_folderpath[-1] == "/":
            remote_filepath = remote_folderpath + zip_filename
        else:
            remote_filepath = remote_folderpath + "/" + zip_filename

        print("sftp.put('" + zip_filepath + "', '" + remote_filepath + "')")
        sftp.put(zip_filepath, remote_filepath)

        print('Closing SFTP connection ...')
        sftp.close()

        print('Unzipping temp file remotely ...')
        remote_unzip_command = 'unzip -qq "' + remote_filepath + '" -d "' + remote_folderpath + '"'
        print(remote_unzip_command)
        stdin, stdout, stderr = ssh_client.exec_command(remote_unzip_command)
        if stdout.channel.recv_exit_status() == 0:
            print(f"Temp file has been successfully unzipped.")
        else:
            print(f"Error unzipping temp file: {stderr.read().decode()}")

        print('Deleting temp file remotely ...')
        remote_rm_command = 'rm "' + remote_filepath + '"'
        print(remote_rm_command)
        stdin2, stdout2, stderr2 = ssh_client.exec_command(remote_rm_command)
        if stdout2.channel.recv_exit_status() == 0:
            print(f"Temp file has been successfully deleted.")
        else:
            print(f"Error deleting temp file: {stderr.read().decode()}")

        print('Closing SSH connection ...')
        ssh_client.close()

        update_status('Upload finished!')
    except Exception as e:
        update_status(str(e))
    finally:
        if is_temporary_zip_file and zip_filepath is not None and os.path.exists(zip_filepath):
            os.remove(zip_filepath)
            print('Temporary local zip file removed.')


def browse_folder():
    local_path = filedialog.askdirectory()
    if local_path == '':
        return
    local_path_entry.delete(0, tk.END)
    local_path_entry.insert(0, local_path)
    upload_button.config(text='Upload folder')
    update_status('Folder selected.')


def browse_zip_file():
    local_path = filedialog.askopenfilename(filetypes=[('ZIP files', '*' + zip_file_extension)])
    if local_path == '':
        return
    local_path_entry.delete(0, tk.END)
    local_path_entry.insert(0, local_path)
    upload_button.config(text='Upload ZIP file')
    update_status('ZIP file selected.')


def upload():
    local_path = local_path_entry.get()
    remote_folder = remote_folder_entry.get()
    hostname = hostname_entry.get()
    username = username_entry.get()
    password = password_entry.get()

    zip_and_upload(local_path, remote_folder, hostname, username, password)


def save_config():
    new_config = configparser.ConfigParser()
    new_config['SFTP'] = {
        'remote_folder': remote_folder_entry.get(),
        'hostname': hostname_entry.get(),
        'username': username_entry.get(),
        'password': password_entry.get(),
    }

    with open(config_filepath, 'w') as file:
        new_config.write(file)

    update_status('Config saved.')


# Create main window
padding = 15
root = tk.Tk()
root.title("Fast SFTP Folder Uploader")
root.geometry('400x400')

# Local folder selection
local_path_label = tk.Label(root, text="Local folder or ZIP file:")
local_path_label.pack()
local_path_entry = tk.Entry(root)
local_path_entry.pack(fill="x", padx=padding)

browse_buttons_frame = tk.Frame(root)
browse_buttons_frame.pack(pady=20)

browse_folder_button = tk.Button(browse_buttons_frame, text="Select folder", command=browse_folder)
browse_folder_button.pack(side="left")
local_path_label = tk.Label(browse_buttons_frame, text="or")
local_path_label.pack(side="left", padx=5, pady=5)
browse_zip_file_button = tk.Button(browse_buttons_frame, text="Select ZIP file", command=browse_zip_file)
browse_zip_file_button.pack(side="left")

# Remote folder and SFTP settings
remote_folder_label = tk.Label(root, text="Remote Folder:")
remote_folder_label.pack()
remote_folder_entry = tk.Entry(root)
remote_folder_entry.pack(fill="x", padx=padding)

hostname_label = tk.Label(root, text="Hostname:")
hostname_label.pack()
hostname_entry = tk.Entry(root)
hostname_entry.pack(fill="x", padx=padding)

username_label = tk.Label(root, text="Username:")
username_label.pack()
username_entry = tk.Entry(root)
username_entry.pack(fill="x", padx=padding)

password_label = tk.Label(root, text="Password:")
password_label.pack()
password_entry = tk.Entry(root, show="*")
password_entry.pack(fill="x", padx=padding)

# Load saved configuration
config = configparser.ConfigParser()
if os.path.exists(config_filepath):
    config.read(config_filepath)
if 'SFTP' in config:
    remote_folder_entry.insert(0, config['SFTP']['remote_folder'])
    hostname_entry.insert(0, config['SFTP']['hostname'])
    username_entry.insert(0, config['SFTP']['username'])
    password_entry.insert(0, config['SFTP']['password'])

# Save config button
save_button = tk.Button(root, text="Save Config", command=save_config)
save_button.pack()

# Upload button
upload_button = tk.Button(root, text="Upload", command=upload)
upload_button.pack()

# Status output label
output_text = StringVar()
output_text.set('Select a local folder or ZIP file to upload.')
output_label = tk.Label(root, textvariable=output_text)
output_label.pack()

root.mainloop()
