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
FILETOWORK="/tmp/fruits"
fruits = ["apple", "pear", "peach", "grape", "banana"]


def filestructure():
    try:
        # Checks if /tmp/fruits is not empty
        if os.path.getsize(FILETOWORK) <= 0:
            print(bcolors.FAIL + FILETOWORK + " " + "seems to be empty" + bcolors.ENDC  )
        else:
            with open(FILETOWORK) as file_content:
                contents = file_content.read()
                for x in contents.splitlines():
                    if fruits[0] in x and fruits[0] in x and fruits[0] in x and  fruits[0] in x and fruits[0] in x: 
                        print(bcolors.OKGREEN + FILETOWORK + " has a proper content"+ bcolors.ENDC)
                    else: 
                        print(bcolors.FAIL + FILETOWORK + " does not have a proper content"+ bcolors.ENDC)
    except FileNotFoundError:
        print(bcolors.FAIL +  FILETOWORK + " is not created"+ bcolors.ENDC)
 # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
