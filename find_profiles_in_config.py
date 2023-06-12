import os
import re
from bcolours import bcolours as bc

def find_in_conf_file():
    path = "~/.aws/config"
    full_path = os.path.expanduser(path)
    latest = ''

    # open file to read
    f1 = open("%s" % full_path, "r")
    #read content of the file
    lines = f1.readlines()
    # move the pointer to the beginning of the file
    f1.seek(0)
    regex = r"\[profile [0-9]{12}_S[0-9a-zA-Z]{8}"
    print(f"\n{bc.OKBLUE}The following AWS account profiles are stored in your local config file.{bc.ENDC}")
    
    # cycle through each line of the config file
    for line in lines:
        if re.match(regex, line):
            print(line[1:-2])
            latest = line[9:-2]
    f1.close()
    return latest

if __name__ == '__main__':
    find_in_conf_file()