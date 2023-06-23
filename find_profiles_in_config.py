import os
import re
from bcolours import bcolours as bc

def find_in_conf_file():
    profiles = []
    path = "~/.aws/config"
    full_path = os.path.expanduser(path)
    latest = ''

    # open file to read
    f1 = open("%s" % full_path, "r")
    #read content of the file
    lines = f1.readlines()
    # move the pointer to the beginning of the file
    f1.seek(0)
    # set regedt to search for profile
    #regex = r"\[profile s[0-9a-zA-Z]{8}-i[0-9a-zA-Z]{2}"
    regex = r"\[profile"

    print(f"\n{bc.OKCYAN}The following AWS account profiles are stored in your local config file.{bc.ENDC}")
    
    # cycle through each line of the config file
    for line in lines:
        if re.match(regex, line):
            print(line[9:-2])
            profiles.append(line[9:-2])
    #        latest = line[9:-2]
    f1.close()
    return profiles

def rtn_sso_values(find_prof):  
    path = "~/.aws/config"
    full_path = os.path.expanduser(path)
    latest = ''
    match = False

    # open file to read
    f1 = open("%s" % full_path, "r")
    #read content of the file
    lines = f1.readlines()
    # move the pointer to the beginning of the file
    f1.seek(0)
    # set regedt to search for profile
    #regex = r"\[profile s[0-9a-zA-Z]{8}-i[0-9a-zA-Z]{2}"
    regex_prof = r"\[profile " + re.escape(find_prof)
    regex_acc = r"sso_account_id = [0-9]{12}"
    regex_name = r"sso_role_name = *"

    print(f"\n{bc.OKCYAN}The following AWS account profiles are stored in your local config file.{bc.ENDC}")
    
    # cycle through each line of the config file
    for line in lines:
        if re.match(regex_prof, line):
            print(line[9:-2])
            match = True

        if match:
            if re.match(regex_acc, line):
                sso_acc = line.removeprefix('sso_account_id = ').removesuffix('\n')

            if re.match(regex_name, line):
                sso_name = line.removeprefix('sso_role_name = ').removesuffix('\n')
                break
    f1.close()
    return sso_acc, sso_name

if __name__ == '__main__':
    rtn_sso_values()
    find_in_conf_file()