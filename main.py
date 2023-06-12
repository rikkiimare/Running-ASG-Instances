import boto3
from botocore.exceptions import ClientError
import os
import sys
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
        # else:
        #     print(f"{bc.WARNING}AWS_PROFILE environment variable is not set.{bc.ENDC}\n{bc.FAIL}The script will exit.{bc.ENDC}")
        #     quit()
    
    # Assign profile to environ var
    os.environ['AWS_PROFILE'] = profile_name
    print(f"\n{bc.HEADER} {os.environ['AWS_PROFILE']} {bc.ENDC}")

    # Works - commented out while working on the ~/.aws/credentials file
    # s3 = boto3.client('s3')
    # response = s3.list_buckets()

    # # Output bucket names
    # for bucket in response['Buckets']:
    #     print(f'    {bucket["Name"]}')
    
    #Assign AutoScalingGroup name to query
    asg = input(f'{bc.OKBLUE}Please input the ASG name you are working with : {bc.ENDC}')

    while 1:
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



        
        # dict_you_want = {key: old_dict[key] for key in your_keys}
        # listkeys = ['AutoScalingGroupName', 'MinSize' ]
        # asg_dict = {key: asg_response['AutoScalingGroups'][0] for key in listkeys}
        instance_ids = []
        instance_vals = []
        asg_dict = {}
        inst_dict = {}

        if len(asg_response['AutoScalingGroups']) != 0:
            for i in asg_response['AutoScalingGroups']:
                asg_dict = {
                    'AutoScalingGroupName': i['AutoScalingGroupName'],
                    'MinSize': i['MinSize'],
                    'MaxSize': i['MaxSize'],
                    'DesiredCapacity': i['DesiredCapacity']
                }
                for k in i['Instances']:
                    inst_dict = {
                        'InstanceId': k['InstanceId'],
                        'InstanceType': k['InstanceType'],
                        'HealthStatus': k['HealthStatus'],
                        'AvailabilityZone': k['AvailabilityZone']
                    }
                    instance_vals.append(inst_dict)
                    instance_ids.append(k['InstanceId'])
            
            asg_dict['Instances'] = instance_vals
            
            print(f"  {bc.OKCYAN} ASG group set to : {bc.ENDC}{bc.WARNING}{bc.BOLD}{asg}{bc.ENDC}{bc.OKCYAN} \t Scaling Min/Desired/Max: {bc.ENDC}{bc.WARNING}{bc.BOLD}{asg_dict['MinSize']}/{asg_dict['DesiredCapacity']}/{asg_dict['MaxSize']}{bc.ENDC}")
            display.setup()

            ec2_response = ec2_client.describe_instances(
                InstanceIds = instance_ids
                )
            
            for i in ec2_response['Reservations']:
                for k in i['Instances']:
                    # display.display(k)
                    for j in asg_dict['Instances']:
                        if k['InstanceId'] == j['InstanceId']:
                            display.display(k,j)
        
            try:
                loop_resp = input("\nPress any key to recheck ASG or Q to exit\n")
            except SyntaxError:
                pass

            if loop_resp == 'Q':
                break
        else:
            print("There seems to be an issue with the ASG group provided.")
            break





