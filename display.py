from bcolours import bcolours as bc
import pytz


def display(asg, inst, indent=1):
      ind = '\t'*indent
      #   state = asg['State']
      dt = asg['LaunchTime'].astimezone(pytz.timezone('Europe/London')).strftime("""%Y-%m-%d %H:%M:%S""")
      #if asg['State']
      if len(asg['State']['Name']) >= 8:
            if 'KeyName' in asg:
                  print(f"{ind}{asg['InstanceId']}{ind}{asg['InstanceType']}{ind}{inst['HealthStatus']}{ind}{ind}{inst['AvailabilityZone']}{ind}{dt}{ind}{asg['State']['Name']}{ind}{asg['KeyName']}")
            else:
                  print(f"{ind}{asg['InstanceId']}{ind}{asg['InstanceType']}{ind}{inst['HealthStatus']}{ind}{ind}{inst['AvailabilityZone']}{ind}{dt}{ind}{asg['State']['Name']}{ind}--")
      else:
            if 'KeyName' in asg:
                  print(f"{ind}{asg['InstanceId']}{ind}{asg['InstanceType']}{ind}{inst['HealthStatus']}{ind}{ind}{inst['AvailabilityZone']}{ind}{dt}{ind}{asg['State']['Name']}{ind}{ind}{asg['KeyName']}")
            else:
                  print(f"{ind}{asg['InstanceId']}{ind}{asg['InstanceType']}{ind}{inst['HealthStatus']}{ind}{ind}{inst['AvailabilityZone']}{ind}{dt}{ind}{asg['State']['Name']}{ind}{ind}--")

def setup(indent=1):
      ind = '\t'*indent
      print(f"{bc.BOLD}{bc.OKGREEN}{ind}Instance Id{ind}{ind}Instance Type{ind}Health Status{ind}AZ{ind}{ind}Launch Date & Time{ind}State{ind}{ind}Key Name{bc.ENDC}")


if __name__ == '__main__':
    setup()