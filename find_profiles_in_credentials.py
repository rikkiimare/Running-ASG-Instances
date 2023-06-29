import os
import re
from bcolours import bcolours as bc

def find_in_cred_file():
    path = "~/.aws/credentials"
    full_path = os.path.expanduser(path)
    latest = ''

    # open file to read
    f1 = open("%s" % full_path, "r")
    #read content of the file
    lines = f1.readlines()
    # move the pointer to the beginning of the file
    f1.seek(0)
    regex = r"\[[0-9]{12}"
    print(f"\n{bc.OKBLUE}The following AWS account profiles are stored in your local credentials file.{bc.ENDC}")
    # cycle through each line of the credentials file
    for line in lines:
        if re.match(regex, line):
            print(line)
            latest = line
    f1.close()


    return latest[1:-2]

if __name__ == '__main__':
    find_in_cred_file()