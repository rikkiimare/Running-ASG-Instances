import boto3
from botocore.exceptions import ClientError
#import os
from datetime import datetime
from bcolours import bcolours as bc


import find_profiles_in_config
import display
import sys

if __name__ == '__main__':
    
    find_profiles_in_config.find_in_conf_file()

    prof_name = input(f'{bc.OKBLUE}Please input the profile listed above you would like to use : {bc.ENDC}')
    
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





