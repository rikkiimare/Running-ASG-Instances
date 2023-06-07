import boto3
from botocore.exceptions import ClientError
import os
from datetime import datetime
from bcolours import bcolours as bc

import amend_aws_cred
import find_profiles_in_credentials
import display

if __name__ == '__main__':
    
    # identify all account profiles within local credentials file
    profile_name = find_profiles_in_credentials.find_in_cred_file()

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
        
    else:
        if "AWS_PROFILE" in os.environ:
            print(f"{bc.OKBLUE}The script will continue with the currently set AWS_PROFILE.{bc.ENDC}")
        else:
            print(f"{bc.WARNING}AWS_PROFILE environment variable is not set.{bc.ENDC}\n{bc.FAIL}The script will exit.{bc.ENDC}")
            quit()
    
    # Assign profile to environ var
    os.environ['AWS_PROFILE'] = profile_name
    print(f"\n{bc.HEADER} {os.environ['AWS_PROFILE']} {bc.ENDC}")

    # Works - commented out while working on the ~/.aws/credentials file
    # s3 = boto3.client('s3')
    # response = s3.list_buckets()

    # # Output bucket names
    # for bucket in response['Buckets']:
    #     print(f'    {bucket["Name"]}')
    
    asg = input(f'{bc.OKBLUE}Please input the ASG name you are working with : {bc.ENDC}')
    try:
        asg_client = boto3.client('autoscaling', region_name='eu-west-2')
    except ClientError as e:
        print(e)
        print(f"{bc.FAIL} There may be an issue with your credentials{bc.ENDC}")
        sys.exit(1)

    try:
        ec2_client = boto3.client('ec2', region_name='eu-west-2')
    except ClientError as e:
        print(e)
        print(f"{bc.FAIL} There may be an issue with your credentials{bc.ENDC}")
        sys.exit(1)

    try:
        asg_response = asg_client.describe_auto_scaling_groups(AutoScalingGroupNames=[asg])
    except Exception as ex:
        print(f"Error - {ex}")
        print(f"{bc.FAIL} There may be an issue with the ASG name you entered{bc.ENDC}")
        sys.exit(1)

    instance_ids = []

    print(f"  {bc.OKCYAN} ASG group set to : {asg} {bc.ENDC}")
    display.setup()

    for i in asg_response['AutoScalingGroups']:
        for k in i['Instances']:
            #print(f"{k['InstanceId']}, {k['InstanceType']}, {k['LifecycleState']}, {k['HealthStatus']}, {k['AvailabilityZone']}")
            instance_ids.append(k['InstanceId'])
    
    ec2_response = ec2_client.describe_instances(
        InstanceIds = instance_ids
        )
    
    for i in ec2_response['Reservations']:
        for k in i['Instances']:
            display.display(k)




