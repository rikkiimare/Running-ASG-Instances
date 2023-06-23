import boto3
from botocore.exceptions import ClientError
import subprocess
import os
import sys
import re
from datetime import datetime
from bcolours import bcolours as bc

import amend_aws_cred
import find_profiles_in_config
import find_profiles_in_credentials
import elevate_permissions
import display

# Variable declaration
yes_choices = ['yes', 'y', 'Y', 'YES']
w_choices = ['1', '2']
auth_choices = ['cred', 'sso', 'nr']
quit_choices = ['Q', 'q', 'quit', 'QUIT']
cw_group = ''
cw_grep = ''
e_exit = ''

def re_pop_aws_config():
    path = "~/.aws/sso-store"
    full_path = os.path.expanduser(path)

    try:
        f = open(full_path)
        f.close()
    except FileNotFoundError as e:
        print(e)
    else:
        cmd = subprocess.run([f"cat ~/.aws/sso-store >> ~/.aws/config"],
            shell=True,
            check=True,
            capture_output=True,
        )

def get_caller_attributes():
    caller_id = subprocess.Popen("aws sts get-caller-identity --profile default",
               stdout=subprocess.PIPE,  #TODO: build in err functionality
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

def check_config_file_len():
    path = "~/.aws/config"
    full_path = os.path.expanduser(path)

    # open file to read
    f1 = open("%s" % full_path, "r")
    return len(f1.readlines())

def profile_selection():
    # ~/.aws/config file is stripped out when perms are elevated.  call a function to move the contents of ~/.aws/sso-store file back into ~/.aws/config
    conf_len = check_config_file_len()
    
    if conf_len < 10:
        re_pop_aws_config()
    
    # Look in the ~/.aws/config file and identify the available profiles, print each profile to terminal
    profiles = find_profiles_in_config.find_in_conf_file()
    
    # As user which of the profile to use
    while 1:
        prof_name = input(f'{bc.OKBLUE}\nPlease select and input one of the profile listed above you would like to use : {bc.ENDC}')
        if prof_name in profiles:
            break
        else:
            print(f"{bc.FAIL}{bc.FAIL}Please enter a valid profile from the list above.{bc.ENDC}")            
    return prof_name

def report_asg_ec2_status(asg):
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

    return ec2_client, instance_ids, asg_dict

def print_asg_details(ec2_client, instance_ids, asg_dict):
    
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

def event_log_report(instance_ids, group, grep):
    
    #group = "production-BANK-VDTE-log"
    #group = 'stage-WAF-messages'
    #grep = "Sending"
    # Set regex to remove ip addresses from output messages
    ip_addr_regex = re.compile(r'\b(?:[0-9]{1,3}[\-\.]{1}){3}[0-9]{1,3}\b')
    #instance_ids = ['i-0a3ee4a22422b9f81']
    #instance_ids = ['i-0474c0534cc15e091', 'i-0c9ffb6a99f7577d9']

    aged_20m = int((datetime.now().timestamp() - 1200) * 1000)
    millisec = int(datetime.now().timestamp() * 1000)

    logs_client = session.client('logs', region_name='eu-west-2')

    print(f"{bc.WARNING}Log Group Name - {group}{bc.ENDC}")
    for instance in instance_ids:
        print(f"\n {bc.OKGREEN}Instance - {instance}{bc.ENDC}")
        responses = logs_client.get_log_events(
            logGroupName=group,
            logStreamName=instance,
            startTime=aged_20m,
            endTime=millisec,
            limit=49
            )

        for events in responses['events']:
            if grep in events['message']:
                print(f"  {re.sub(ip_addr_regex, '', events['message'])}")

def attribute_grep_setting():
    pass

if __name__ == '__main__':
    
    """
    DONE: Ask user if they want to use the new 'AWS IAM Identity Center' (.aws/config) or old pasting into (.aws/credentials) way of auth
    DONE: Bring in code from main branch for old auth
    DONE: New method - list profiles in (/.aws/config) DONE
          Use sso_role_name and sso_account_id to elevate perms
    DONE: Possible need to use sso-store and copy contents into .aws/config after elevation of privileges
    DONE: Run the exec_login function above.
    DONE: a check to see if files exist.. e.g. ~/.aws/sso-store
    """

    i = 0
    # DONE: Need a warning that before this script is run the user needs to be logged into AWS SSO

    while 1:
        iresponse = input(f"{bc.OKCYAN}\nHow would you like to authenticate ? \n\t \
                          Add new credentials respond {bc.ENDC}{bc.OKGREEN}'cred'{bc.ENDC}{bc.OKCYAN}:\n\t \
                          Use 'AWS IAM Identity Center' respond {bc.ENDC}{bc.OKGREEN}'sso'{bc.ENDC}{bc.OKCYAN}: \n\t \
                          Don't need to authenticate, just want to select an  profile respond {bc.ENDC}{bc.OKGREEN}'nr'{bc.ENDC}{bc.OKCYAN}: \n\t{bc.ENDC} \
                          ")
        if iresponse.lower() in auth_choices:
            break
        else:
            print(f"{bc.FAIL}The only responses available are 'cred', 'sso' or 'nr'!{bc.ENDC}")

    if iresponse == 'cred':
        # identify all account profiles within local credentials file
        prof_name = find_profiles_in_credentials.find_in_cred_file()

        # Display the last modified time to the screen
        amend_aws_cred.time_cred_file_mod()

        # Call module to accept credentials from user

        user_resp = input(f'{bc.OKCYAN}Do you want to amend the local .aws\credentials file? (yes/no): {bc.ENDC}')
        if user_resp.lower() in yes_choices:
            creds = amend_aws_cred.accept_creds()

            # Remove the old credentials out of the ~/.aws/credentials file
            amend_aws_cred.rm_cred_from_env(creds)

            # Add new credentials provided into the ~/.aws/credentials file
            prof_name = amend_aws_cred.set_cred_from_env(creds)    
        else:
            if "AWS_PROFILE" in os.environ:
                print(f"{bc.OKCYAN}The script will continue with the currently set AWS_PROFILE.{bc.ENDC}")
            # else:
            #     print(f"{bc.WARNING}AWS_PROFILE environment variable is not set.{bc.ENDC}\n{bc.FAIL}The script will exit.{bc.ENDC}")
            #     quit()
        
        # Assign profile to environ var
        os.environ['AWS_PROFILE'] = prof_name
        print(f"\n{bc.HEADER} {os.environ['AWS_PROFILE']} {bc.ENDC}")
    elif iresponse == 'sso':
        # Use the profile_selection fuction to populate prof_name var
        prof_name = profile_selection()

        # Use the profile name selected to identify the account_id and role associated.
        sso_acc_id, sso_role_name = find_profiles_in_config.rtn_sso_values(prof_name)

        # Attempt a get-caller-identity with the default profile to retrieve assigner and username attributes
        # Assign default profile to environ var
        os.environ['AWS_PROFILE'] = 'default'
        exec_login('default')
        sso_assigner, sso_user = get_caller_attributes()

        # Use sso_role_name and sso_account_id to elevate perms
        elevate_permissions.elevate_perms(sso_acc_id, sso_role_name, sso_assigner, sso_user)

        # ~/.aws/config file is stripped out when perms are elevated.  call a function to move the contents of ~/.aws/sso-store file back into ~/.aws/config
        re_pop_aws_config()

        # Login as a profile to AWS
        exec_login(prof_name)
    elif iresponse == 'nr':
        # Use the profile_selection fuction to populate prof_name var
        prof_name = profile_selection()
            

    # Set sso credentials
    session = boto3.session.Session(profile_name=prof_name)


    #Assign AutoScalingGroup name to query
    asg = input(f'{bc.OKCYAN}Please input the ASG name you are working with : {bc.ENDC}')

    while i != 1:
        wresponse = input(f"\n{bc.OKCYAN}What would you like to check? \n\t\
                          Enter 1 - to check AutoScaling Group \n\t\
                          Enter 2 - to check the Cloudwatch logs {bc.ENDC}\n\t\
                          {bc.OKBLUE}If you would like to exit the script input 'Q'{bc.ENDC}\n\t\
                          ")
                        # DONE: If you select option 2 the first time through there is nothing in the instance varibale
        if wresponse in w_choices:
            if wresponse == '1':
                while 1:
                    #TODO: Put in a if loop to either look at the ASG or the logs
                    instances = []
                    ec2_client, instances, asg_dict = report_asg_ec2_status(asg)
                    print_asg_details(ec2_client, instances, asg_dict)

                    try:
                        loop_resp = input(f"\n{bc.OKCYAN}Press any key to recheck ASG or 'Q' to go back to the original menu.{bc.ENDC}\n")
                    except SyntaxError:
                        pass

                    if loop_resp in quit_choices:
                        break
            elif wresponse == '2':    
                while 1:
                    ec2_client, instances, asg_dict = report_asg_ec2_status(asg)
                    if cw_group != '':
                        event_log_report(instances, cw_group, cw_grep)
                    else:
                        cw_group = input(f"{bc.OKCYAN}Please input the log group you would like to monitor.{bc.ENDC}\n")
                        cw_grep = input(f"{bc.OKCYAN}Please enter any keywords you would like to search for in your log message.{bc.ENDC}\n")
                        event_log_report(instances, cw_group, cw_grep)
                    
                    try:
                        cw_loop_resp = input(f"\n{bc.OKCYAN}Press any key to recheck CloudWatch logs or 'Q' to go back to the original menu.{bc.ENDC}\n")
                    except SyntaxError:
                        pass

                    if cw_loop_resp in quit_choices:
                        break                    


        else:
            e_exit = input(f"{bc.OKCYAN}Would you like to exit the script? (Y/N){bc.ENDC}\n")
            
        if e_exit in yes_choices:
            i = 1



        




