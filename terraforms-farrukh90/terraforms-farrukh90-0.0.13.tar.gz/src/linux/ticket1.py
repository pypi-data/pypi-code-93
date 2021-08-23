import os 

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
def filestructure():
    # Checks if /tmp/test is created.
    if os.path.isdir("/tmp/test"):
        print(bcolors.OKGREEN + "test Folder is created in /tmp" + bcolors.ENDC)
    else: 
        print(bcolors.FAIL + "test Folder isn't created in /tmp properly, please try again" + bcolors.ENDC)

    # Checks if /tmp/services is created.
    if os.path.isfile("/tmp/services"):
        print(bcolors.OKGREEN + "/tmp/services is created properly" + bcolors.ENDC)
    else: 
        print(bcolors.FAIL + "/tmp/services is not created properly, please try again" + bcolors.ENDC)

    # Checks if /tmp/passwd is created.
    if os.path.isfile("/tmp/passwd"):
        print(bcolors.OKGREEN + "/tmp/passwd is created properly" + bcolors.ENDC)
    else: 
        print(bcolors.FAIL + "/tmp/passwd is not created properly, please try again" + bcolors.ENDC)

    # Checks if /tmp/.secret is created.
    if os.path.isfile("/tmp/.secret"):
        print(bcolors.OKGREEN + "/tmp/.secret is created properly" + bcolors.ENDC)
    else: 
        print(bcolors.FAIL + "/tmp/.secret is not created properly, please try again" + bcolors.ENDC)

    # Checks if /tmp/Photos is created.
    if os.path.isdir("/tmp/Photos") and os.path.isdir("/tmp/Photos/Hawaii") and os.path.isdir("/tmp/Photos/Florida"):
        print(bcolors.OKGREEN + "/tmp/Photos is created with a proper content" + bcolors.ENDC)
    else: 
        print(bcolors.FAIL + "/tmp/Photos is not created with a proper content, please try again" + bcolors.ENDC)
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 


