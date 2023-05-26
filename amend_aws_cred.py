from datetime import date
import os

def set_cred_from_env(creds):
    today = date.today()

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
    count = 4
    for line in lines:
        count += 1
        if line != aws_profile_name and count > 3:
            f1.write(line)
        elif line == aws_profile_name:
            count = 0
    f1.truncate()
    f1.close()

if __name__ == '__main__':
    set_cred_from_env()