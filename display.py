from bcolours import bcolours as bc

def display(asg, inst, indent=1):
      ind = '\t'*indent
      #   state = asg['State']

      if 'KeyName' in asg:
            print(f"{ind}{asg['InstanceId']}{ind}{asg['InstanceType']}{ind}{inst['HealthStatus']}{ind}{ind}{inst['AvailabilityZone']}{ind}{asg['LaunchTime']}{ind}{asg['State']['Name']}{ind}{ind}{asg['KeyName']}")
      else:
            print(f"{ind}{asg['InstanceId']}{ind}{asg['InstanceType']}{ind}{inst['HealthStatus']}{ind}{ind}{inst['AvailabilityZone']}{ind}{asg['LaunchTime']}{ind}{asg['State']['Name']}{ind}{ind}--")

def setup(indent=1):
      ind = '\t'*indent
      print(f"{bc.BOLD}{bc.OKGREEN}{ind}Instance Id{ind}{ind}Instance Type{ind}Health Status{ind}AZ{ind}{ind}Launch Date & Time{ind}{ind}State{ind}{ind}Key Name{bc.ENDC}")


if __name__ == '__main__':
    setup()