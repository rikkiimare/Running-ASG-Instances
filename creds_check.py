import boto3
import os
import amend_aws_cred
from datetime import datetime

def accept_creds():
    print("Enter/Paste your content. Ctrl-D or Ctrl-Z ( windows ) to save it.")
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
    dt = datetime.fromtimestamp(statbuf.st_mtime)
    cdt = datetime.now()

    dt_str = dt.strftime( "%d-%m-%Y @ %H:%M:%S" )
    time_diff = cdt - dt

    print(f"Last time /.aws/credentials was modified {dt_str} which is {time_diff.total_seconds() // 60} minutes ago")

if __name__ == '__main__':
    
    # Display the last modified time to the screen
    time_cred_file_mod()

    # Call module to accept credentials from user
    creds = accept_creds()
    
    amend_aws_cred.rm_cred_from_env(creds)

    profile_name = amend_aws_cred.set_cred_from_env(creds)
    
    os.environ['AWS_PROFILE'] = profile_name
    print(os.environ['AWS_PROFILE'])

    # Works - commented out while working on the ~/.aws/credentials file
    s3 = boto3.client('s3')
    response = s3.list_buckets()

    # Output bucket names
    for bucket in response['Buckets']:
        print(f'    {bucket["Name"]}')

