from bcolours import bcolours as bc

def display(self, indent=1):
        ind = '\t'*indent
        state = self['State']
        print(f"{ind}{self['InstanceId']}{ind}{self['InstanceType']}{ind}{self['LaunchTime']}{ind}{self['KeyName']}{ind}{state['Name']}")

def setup(indent=1):
      ind = '\t'*indent
      print(f"{bc.BOLD}{bc.OKGREEN}{ind}Instance Id{ind}{ind}Instance Type{ind}Launch Date & Time{ind}{ind}Key Name{ind}State{bc.ENDC}")


if __name__ == '__main__':
    display(self)