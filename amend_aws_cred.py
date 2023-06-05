from datetime import datetime
import os
from bcolours import bcolours as bc

def set_cred_from_env(creds):
    today = datetime.today()

    aws_profile_name = creds[0]
    aws_access_key_id = creds[1]
    # val = val.split("=")
    # aws_access_key_id = val[1]
    aws_secret_access_key = creds[2]
    aws_session_token = creds[3]

    # amend credentials file
    path = "~/.aws/credentials"
    full_path = os.path.expanduser(path)
    print(full_path)

    f1 = open("%s" % full_path, "a")
    f1.write("\n" + str(aws_profile_name) + "\n")
    f1.write(str(aws_access_key_id) + "\n")
    f1.write(str(aws_secret_access_key) + "\n")
    f1.write(str(aws_session_token) + "\n\n")
    f1.close
    
    # remove sq brackets from profile name
    aws_profile_name = aws_profile_name.replace("[", "")
    aws_profile_name = aws_profile_name.replace("]", "")

    return aws_profile_name

def rm_cred_from_env(creds):
    content = []
    aws_profile_name = creds[0]
    aws_profile_name = aws_profile_name + "\n"
    # amend credentials file
    path = "~/.aws/credentials"
    full_path = os.path.expanduser(path)
    
    # open file to read
    f1 = open("%s" % full_path, "r+")
    #read content of the file
    lines = f1.readlines()
    # move the pointer to the beginning of the file
    f1.seek(0)

    # Set count to ensure first if passes the first time through
    count = 4
    for line in lines:
        count += 1
        if line != aws_profile_name and count > 3:
            f1.write(line)
        elif line == aws_profile_name:
            count = 0
    f1.truncate()
    f1.close()

def accept_creds():
    # Take in input from user
    print(f"{bc.OKGREEN}Enter/Paste your credentials content. Once done press Ctrl-D to save it.{bc.ENDC}")
    contents = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        contents.append(line)
    return contents

def time_cred_file_mod():
    path = "~/.aws/credentials"
    full_path = os.path.expanduser(path)
    statbuf = os.stat(full_path)

    # Get the last modified time from the file
    dt = datetime.fromtimestamp(statbuf.st_mtime)
    # Get current time
    cdt = datetime.now()

    # Change the format of file last modify time
    dt_str = dt.strftime( "%d-%m-%Y @ %H:%M:%S" )
    # Set difference in time between now and last modify
    time_diff = cdt - dt

    if time_diff.total_seconds() // 60 > 60:
        print(f"{bc.FAIL}/.aws/credentials was last modified at {dt_str} which is {time_diff.total_seconds() // 60} minutes ago\n{bc.ENDC}")
    else:
        print(f"{bc.WARNING}/.aws/credentials was last modified at {dt_str} which is {time_diff.total_seconds() // 60} minutes ago\n{bc.ENDC}")

if __name__ == '__main__':
    set_cred_from_env()