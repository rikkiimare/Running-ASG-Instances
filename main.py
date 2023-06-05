import boto3
import os
from datetime import datetime
from bcolours import bcolours as bc

import amend_aws_cred
import find_profiles_in_credentials

if __name__ == '__main__':
    
    # identify all account profiles within local credentials file
    find_profiles_in_credentials.find_in_cred_file()

    # Display the last modified time to the screen
    amend_aws_cred.time_cred_file_mod()

    # Call module to accept credentials from user
    yes_choices = ['yes', 'y']

    user_resp = input(f'{bc.OKBLUE}Do you want to amend the local .aws\credentials file? (yes/no): {bc.ENDC}')
    if user_resp.lower() in yes_choices:
        creds = amend_aws_cred.accept_creds()

        # Remove the old credentials out of the ~/.aws/credentials file
        amend_aws_cred.rm_cred_from_env(creds)

        # Add new credentials provided into the ~/.aws/credentials file
        profile_name = amend_aws_cred.set_cred_from_env(creds)
        
        # Assign profile to environ var
        os.environ['AWS_PROFILE'] = profile_name
    else:
        if "AWS_PROFILE" in os.environ:
            print(f"{bc.OKBLUE}The script will continue with the currently set AWS_PROFILE ={bc.ENDC}{bc.HEADER} {os.environ['AWS_PROFILE']} {bc.ENDC}")
        else:
            print(f"{bc.WARNING}AWS_PROFILE environment variable is not set.{bc.ENDC}\n{bc.FAIL}The script will exit.{bc.ENDC}")
            quit()
    

    print(f"{bc.HEADER} {os.environ['AWS_PROFILE']} {bc.ENDC}")

    # Works - commented out while working on the ~/.aws/credentials file
    # s3 = boto3.client('s3')
    # response = s3.list_buckets()

    # # Output bucket names
    # for bucket in response['Buckets']:
    #     print(f'    {bucket["Name"]}')

    client = boto3.client('autoscaling', region_name='eu-west-2')
    # response = client.describe_auto_scaling_groups(AutoScalingGroupNames=['integration-production-iig-waf'])
    response = client.describe_auto_scaling_instances()
    print(response)
