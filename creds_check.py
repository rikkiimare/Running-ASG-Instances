import boto3
import os
import amend_aws_cred
from datetime import datetime

class bcolours:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def accept_creds():
    # Take in input from user
    print(f"{bcolours.OKGREEN}Enter/Paste your credentials content. Once done press Ctrl-D to save it.{bcolours.ENDC}")
    contents = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        contents.append(line)
    return contents

def time_cred_file_mod():
    path = "~/.aws/credentials"
    full_path = os.path.expanduser(path)
    statbuf = os.stat(full_path)

    # Get the last modified time from the file
    dt = datetime.fromtimestamp(statbuf.st_mtime)
    # Get current time
    cdt = datetime.now()

    # Change the format of file last modify time
    dt_str = dt.strftime( "%d-%m-%Y @ %H:%M:%S" )
    # Set difference in time between now and last modify
    time_diff = cdt - dt

    print(f"{bcolours.WARNING}Last time /.aws/credentials was modified {dt_str} which is {time_diff.total_seconds() // 60} minutes ago{bcolours.ENDC}")

if __name__ == '__main__':
    
    # Display the last modified time to the screen
    time_cred_file_mod()

    # Call module to accept credentials from user
    creds = accept_creds()
    
    # Remove the old credentials out of the ~/.aws/credentials file
    amend_aws_cred.rm_cred_from_env(creds)

    # Add new credentials provided into the ~/.aws/credentials file
    profile_name = amend_aws_cred.set_cred_from_env(creds)
    
    # Assign profile to environ var
    os.environ['AWS_PROFILE'] = profile_name
    print(os.environ['AWS_PROFILE'])

    # Works - commented out while working on the ~/.aws/credentials file
    s3 = boto3.client('s3')
    response = s3.list_buckets()

    # Output bucket names
    for bucket in response['Buckets']:
        print(f'    {bucket["Name"]}')

