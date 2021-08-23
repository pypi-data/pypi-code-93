import os 
REPONAME="something"
TASK="ec2"

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

def filestructure(REPONAME,TASK):
    """
        This is a documentation for doc.
    """
    # /usr/bin/env python
    if os.path.isdir(REPONAME):
        print(bcolors.OKGREEN + "Repository cloned properly" + bcolors.ENDC)
    # Checks if .gitignore is created.
    if os.path.isfile(REPONAME + "/.gitignore"):
        print(bcolors.OKGREEN + ".gitignore file created properly" + bcolors.ENDC)
    else: 
        print(bcolors.FAIL + ".gitignore file isn't created properly, please try again" + bcolors.ENDC)

    # Checks if README is created.
    if os.path.isfile(REPONAME+ "/README.md"):
        print(bcolors.OKGREEN + "README file created properly" + bcolors.ENDC)
    else: 
        print(bcolors.FAIL + "README file isn't created properly, please try again" + bcolors.ENDC)

    # Checks if the route53 folder is created.
    if os.path.isdir(REPONAME+ "/" + TASK):
        print(bcolors.OKGREEN + "route53 folder is created properly" + bcolors.ENDC)
    else: 
        print(bcolors.FAIL + "route53 isn't created or not named properly, please try again" + bcolors.ENDC)

    # Checks if .gitignore is created in route53 folder.
    if os.path.isfile(REPONAME+ "/" + TASK + "/.gitignore"):
        print(bcolors.OKGREEN + ".gitignore  file is  created in route53 folder properly" + bcolors.ENDC)
    else: 
        print(bcolors.FAIL + ".gitignore file isn't created in route53 folder properly, please try again" + bcolors.ENDC)

    # Checks if .gitignore is created in route53 folder.
    if os.path.isfile(REPONAME+ "/" + TASK + "/README.md"):
        print(bcolors.OKGREEN + "README file created in route53 folder properly" + bcolors.ENDC)
    else: 
        print(bcolors.FAIL + "README file isn't created in route53 folder properly, please try again" + bcolors.ENDC)

    # Checks if .gitignore is created in route53 folder.
    if os.path.isfile(REPONAME+ "/" + TASK + "/provider.tf"):
        print(bcolors.OKGREEN + "provider.tf file created in route53 folder properly" + bcolors.ENDC)
    else: 
        print(bcolors.FAIL + "provider.tf file isn't created in route53 folder properly, please try again" + bcolors.ENDC)
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 





def provider(REPONAME,TASK):
    #   provider.tf
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
    try:
        # Checks if provider has region info in route53 folder.
        with open(REPONAME + TASK + "/provider.tf") as file_content:
            contents = file_content.read()
            for x in contents.splitlines():
                if "region" in x:
                    x = Convert(x)
                    x = x.strip()
                    x = x.strip('"')
                    if x == REGION:
                        print(bcolors.OKGREEN + "Region is set properly" + bcolors.ENDC)
                    else: 
                        print(bcolors.FAIL + "Region isn't set properly, please try again" + bcolors.ENDC)
    except FileNotFoundError:
        print(bcolors.FAIL + "provider.tf is not created"+ bcolors.ENDC)
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 



def route53(REPONAME,TASK):
    #   route53.tf
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
    try:
        # Checks resource record.
        with open(REPONAME+ "/" + TASK + "/" + TASK + ".tf") as file_content:
            contents = file_content.read()
            for x in contents.splitlines():
                if "name" in x:
                    if "blog." in x:
                        print(bcolors.OKGREEN + "Resource Record 'blog' is set" + bcolors.ENDC)
                    else: 
                        print(bcolors.FAIL + "Resource Record 'blog' is not set, please try again" + bcolors.ENDC)

                    if "records" in x:
                        if '["127.0.0.1"]' in x:
                            print(bcolors.OKGREEN + "Resource Record 'IP' is set" + bcolors.ENDC)
                    else: 
                        print(bcolors.FAIL + "Resource Record 'IP' is not set, please try again" + bcolors.ENDC)
                        

                    if "zone_id" in x:
                        if 'Z' in x:
                            print(bcolors.OKGREEN + "zone_id is set" + bcolors.ENDC)
                else: 
                    print(bcolors.FAIL + "zone_id is not set, please try again" + bcolors.ENDC)

    except FileNotFoundError:
        print(bcolors.FAIL + "" + TASK + ".tf is not created" + bcolors.ENDC)
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 



def output(REPONAME,TASK):
    #   output.tf
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
    try: 
        # Checks resource record.
        with open(REPONAME+ "/" + TASK + "/output.tf") as file_content:
            contents = file_content.read()
            for x in contents.splitlines():
                if "aws_route53_record.www.zone_id" in x:
                    if '.zone_id' in x:
                        print(bcolors.OKGREEN + "Output Zone ID is set" + bcolors.ENDC)
                else: 
                    print(bcolors.FAIL + "Output Zone ID is not set" + bcolors.ENDC)


                if "aws_route53_record.www.name" in x:
                    if '.name' in x:
                        print(bcolors.OKGREEN + "Output Zone Name is set" + bcolors.ENDC)
                else: 
                    print(bcolors.FAIL + "Output Zone Name is not set" + bcolors.ENDC)


                if "aws_route53_record.www.records" in x:
                    if '.records' in x:
                        print(bcolors.OKGREEN + "Output Zone Record is set" + bcolors.ENDC)
                else: 
                    print(bcolors.FAIL + "Output Zone Record is not set" + bcolors.ENDC)

    except FileNotFoundError:
        print(bcolors.FAIL + "output.tf isn't created in route53 folder, please try again" + bcolors.ENDC)
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 

    else: 
        print(bcolors.FAIL + "Repository isn't cloned properly, please try again!!!" + bcolors.ENDC)



