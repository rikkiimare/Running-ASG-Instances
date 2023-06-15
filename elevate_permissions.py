import subprocess

def elevate_perms(acc, role, assigner, user):
    subprocess.run(["""~/*aws-cli login-and-assign-role \
                        --account {acc} \
                        --username {user} \
                        --permission-set {role} \
                        --assigner-permission-set {assigner} \
                        --duration-hours 8 """],
               shell=True,
               check=True,
               capture_output=True)
    
if __name__ == '__main__':
    elevate_perms()