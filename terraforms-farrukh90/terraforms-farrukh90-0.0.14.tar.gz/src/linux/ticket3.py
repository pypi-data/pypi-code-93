import os 
import time 

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



# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
def filestructure():
    try:
        FILETOWORK="/tmp/ordered.txt"
        COUNTED_SERVICES = "12391"
        # Checks if "/tmp/ordered.txt" is created
        if os.path.getsize(FILETOWORK) <= 0:
            print(bcolors.FAIL + FILETOWORK + " " + "seems to be empty" + bcolors.ENDC  )
            time.sleep(0.5)
        else:
            print(bcolors.OKGREEN + FILETOWORK + " " + "is created" + bcolors.ENDC  )
            time.sleep(0.5)

        with open(FILETOWORK) as file_content:
            contents = file_content.read()
            for x in contents.splitlines():
                pass 
            last_line = x
            clean_last_line = x.strip()
            if clean_last_line[0].isdigit():
                print(bcolors.OKGREEN + FILETOWORK + " " + "is numerated properly" + bcolors.ENDC  )
            else:
                print(bcolors.FAIL + FILETOWORK + " " + "is not numerated properly" + bcolors.ENDC  )
    except FileNotFoundError:
        print(bcolors.FAIL +  FILETOWORK + " is not created"+ bcolors.ENDC)
    time.sleep(0.5)
 # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 


    try:
        FILETOWORK="/tmp/head.txt"
        num_lines = sum(1 for line in open(FILETOWORK))
        # Checks if "/tmp/head.txt" is created
        if os.path.getsize(FILETOWORK) <= 0 and num_lines == 50:
            print(bcolors.FAIL + FILETOWORK + " " + "seems to be empty" + bcolors.ENDC  )
        else:
            print(bcolors.OKGREEN + FILETOWORK + " " + "is created" + bcolors.ENDC  )
            time.sleep(0.5)

        with open(FILETOWORK) as file_content:
            contents = file_content.read()
            for x in contents.splitlines():
                pass 
            last_line = x
            clean_last_line = x.strip()
            if clean_last_line[0].isdigit():
                print(bcolors.OKGREEN + FILETOWORK + " " + "is numerated properly" + bcolors.ENDC  )
            else:
                print(bcolors.FAIL + FILETOWORK + " " + "is not numerated properly" + bcolors.ENDC  )
    except FileNotFoundError:
        print(bcolors.FAIL +  FILETOWORK + " is not created"+ bcolors.ENDC)

    time.sleep(0.5)
    try:
        FILETOWORK="/tmp/tail.txt"
        num_lines = sum(1 for line in open(FILETOWORK))
        # Checks if "/tmp/tail.txt" is created
        if os.path.getsize(FILETOWORK) <= 0 and num_lines == 50:
            print(bcolors.FAIL + FILETOWORK + " " + "seems to be empty" + bcolors.ENDC  )
        else:
            print(bcolors.OKGREEN + FILETOWORK + " " + "is created" + bcolors.ENDC  )

        with open(FILETOWORK) as file_content:
            contents = file_content.read()
            for x in contents.splitlines():
                pass 
            last_line = x
            clean_last_line = x.strip()
            if clean_last_line[0].isdigit():
                print(bcolors.OKGREEN + FILETOWORK + " " + "is numerated properly" + bcolors.ENDC  )
            else:
                print(bcolors.FAIL + FILETOWORK + " " + "is not numerated properly" + bcolors.ENDC  )
    except FileNotFoundError:
        print(bcolors.FAIL +  FILETOWORK + " is not created"+ bcolors.ENDC)
    time.sleep(0.5)

   
    try:
        FILETOWORK="/tmp/lines.txt"
        num_lines = sum(1 for line in open(FILETOWORK))
        # Checks if "/tmp/lines.txt" is created
        if os.path.getsize(FILETOWORK) <= 0 and num_lines == 250:
            print(bcolors.FAIL + FILETOWORK + " " + "seems to be empty" + bcolors.ENDC  )
        else:
            print(bcolors.OKGREEN + FILETOWORK + " " + "is created" + bcolors.ENDC  )

        with open(FILETOWORK) as file_content:
            contents = file_content.read()
            for x in contents.splitlines():
                pass 
            last_line = x
            clean_last_line = x.strip()
            if clean_last_line[0].isdigit():
                print(bcolors.OKGREEN + FILETOWORK + " " + "is numerated properly" + bcolors.ENDC  )
            else:
                print(bcolors.FAIL + FILETOWORK + " " + "is not numerated properly" + bcolors.ENDC  )

    except FileNotFoundError:
        print(bcolors.FAIL +  FILETOWORK + " is not created"+ bcolors.ENDC)
    time.sleep(0.5)
 # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
