import boto3
from botocore.exceptions import ClientError
import subprocess
import os
import sys
from datetime import datetime
from bcolours import bcolours as bc

import amend_aws_cred
import find_profiles_in_config
import find_profiles_in_credentials
import elevate_permissions
import display

def re_pop_aws_config():
    cmd = subprocess.run([f"cat ~/.aws/sso-store >> ~/.aws/config"],
        shell=True,
        check=True,
        capture_output=True,
    )

def get_caller_attributes():
    caller_id = subprocess.Popen("aws sts get-caller-identity",
               stdout=subprocess.PIPE,
               shell=True,
               )

    output = caller_id.stdout.readlines()

    string = ' '.join(map(str, output))
    assigner = string[string.rfind('SSO_')+4:string.rfind('_')]
    username = string[string.rfind('/')+1:string.rfind('"')]
    return assigner, username

def exec_login(sso_profile):
    return subprocess.run(
        [f"aws sso login --profile {sso_profile}"],
        shell=True,
        check=True,
        capture_output=True,
    )

if __name__ == '__main__':
    
    """
    X: Ask user if they want to use the new 'AWS IAM Identity Center' (.aws/config) or old pasting into (.aws/credentials) way of auth
    X: Bring in code from main branch for old auth
    TODO: New method - list profiles in (/.aws/config) DONE
          Use sso_role_name and sso_account_id to elevate perms
    TODO: Possible need to use sso-store and copy contents into .aws/config after elevation of privileges
    TODO: Run the exec_login function above.
    """
    iresponse = input(f"{bc.OKBLUE}\nWould you like to authenticate by adding new credentials respond 'cred', or using 'AWS IAM Identity Center' respond 'sso'? : {bc.ENDC}")

    if iresponse == 'cred':
        # identify all account profiles within local credentials file
        prof_name = find_profiles_in_credentials.find_in_cred_file()

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
            prof_name = amend_aws_cred.set_cred_from_env(creds)    
        else:
            if "AWS_PROFILE" in os.environ:
                print(f"{bc.OKBLUE}The script will continue with the currently set AWS_PROFILE.{bc.ENDC}")
            # else:
            #     print(f"{bc.WARNING}AWS_PROFILE environment variable is not set.{bc.ENDC}\n{bc.FAIL}The script will exit.{bc.ENDC}")
            #     quit()
        
        # Assign profile to environ var
        os.environ['AWS_PROFILE'] = prof_name
        print(f"\n{bc.HEADER} {os.environ['AWS_PROFILE']} {bc.ENDC}")
    elif iresponse == 'sso':
        # Look in the ~/.aws/config file and identify the available profiles, print each profile to terminal
        find_profiles_in_config.find_in_conf_file()
        
        # As user which of the profile to use
        prof_name = input(f'{bc.OKBLUE}\nPlease input the profile listed above you would like to use : {bc.ENDC}')

        # Use the profile name selected to identify the account_id and role associated.
        sso_acc_id, sso_role_name = find_profiles_in_config.rtn_sso_values(prof_name)

        # Attempt a get-caller-identity with the default profile to retrieve assigner and username attributes
        # Assign default profile to environ var
        os.environ['AWS_PROFILE'] = 'default'
        sso_assigner, sso_user = get_caller_attributes()

        # Use sso_role_name and sso_account_id to elevate perms
        elevate_permissions.elevate_perms(sso_acc_id, sso_role_name, sso_assigner, sso_user)

        # ~/.aws/config file is stripped out when perms are elevated.  call a function to move the contents of ~/.aws/sso-store file back into ~/.aws/config
        re_pop_aws_config()

        # Login as a profile to AWS
        exec_login(prof_name)
        



    # Set sso credentials
    session = boto3.session.Session(profile_name=prof_name)

    #Assign AutoScalingGroup name to query
    asg = input(f'{bc.OKBLUE}Please input the ASG name you are working with : {bc.ENDC}')

    while 1:
        try:
            asg_client = session.client('autoscaling', region_name='eu-west-2')
        except ClientError as e:
            print(e)
            print(f"{bc.FAIL} There may be an issue with your credentials{bc.ENDC}")
            sys.exit(1)

        try:
            ec2_client = session.client('ec2', region_name='eu-west-2')
        except ClientError as e:
            print(e)
            print(f"{bc.FAIL} There may be an issue with your credentials{bc.ENDC}")
            sys.exit(1)

        try:
            asg_response = asg_client.describe_auto_scaling_groups(AutoScalingGroupNames=[asg])
        except Exception as ex:
            print(f"Error - {ex}")
            print(f"{bc.FAIL} There may be an issue with your credentials or the ASG name you entered{bc.ENDC}")
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
                loop_resp = input("\nPress any key to recheck ASG or 'Q' to exit\n")
            except SyntaxError:
                pass

            if loop_resp == 'Q':
                break
        else:
            print("There seems to be an issue with the ASG group provided.")
            break





