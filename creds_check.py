import boto3
import os
import amend_aws_cred

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

if __name__ == '__main__':
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

