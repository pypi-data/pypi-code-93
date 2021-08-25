import sys
from os import listdir
from os.path import isdir, join
import gitlab
import os
import pathlib
import subprocess
import shutil

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
pathList=[]
failedloglist=[]
logsFolder=""
printLogs=False
linesList =[]
listt=[]
logfileName =[]
state_list =""
def getAllFolder(path):
    if  path in pathList:
        return
    else:
        # pathList.append(path)
        only_tf_files=[f for f in  sorted(listdir(path)) if not isdir(join(path, f)) and f.endswith('.tf')]
        if len(only_tf_files)==0:
            onlyDirectories = [d for d in sorted(listdir(path)) if isdir(join(path, d)) and d !=".terraform" and d != ".terragrunt-cache"]
            if(len(onlyDirectories) > 0):
                for i in range(0, len(onlyDirectories)):
                    getAllFolder(path+"/"+onlyDirectories[i])
        else :
            pathList.append(path)
    return pathList


def executeTerragrunt(command ,path,logsFolder,logfileName ):

     logfileName=path.split("live/")[1].replace("/","_")
     profile = "dev02"
     if("20-int" in path) : profile = "int"
     if("30-uat" in path) : profile = "uat"
     if("31-uatm" in path) : profile = "uat"
     if("32-miscuat" in path) : profile = "miscuat"
     if("42-miscprod" in path) : profile = "miscprod"
     if("40-prod" in path) : profile = "prod"
     if("41-proddr" in path) : profile = "prod"
     state_list = (" export AWS_PROFILE="+profile+" && terragrunt "+command+" -no-color 2>&1 | tee " +logsFolder+"/"+logfileName+".log")
     return state_list


def printlog(command ,pathList ,logsFolder ,printLogs):
    for path in pathList:
         print(bcolors.OKBLUE+path+":" +bcolors.ENDC)
         os.chdir(path)
         popen = subprocess.Popen(executeTerragrunt(command ,path,logsFolder,logfileName), stdout = subprocess.PIPE, shell = True, encoding = 'utf8')
         lines = popen.stdout.readlines()
         popen.stdout.close()
         for line in lines:
             if("No changes. Infrastructure is up-to-date." in line):
                 print(bcolors.OKGREEN +"  : No changes. Infrastructure is up-to-date."+ bcolors.ENDC)
                 continue
             if("No changes. Your infrastructure matches the configuration." in line):
                 print(bcolors.OKGREEN +"  : No changes. Your infrastructure matches the configuration."+ bcolors.ENDC)
                 continue
             if("Plan:" in line):
                 print(bcolors.WARNING +line+ bcolors.ENDC)
                 continue
             if ("will be updated in-place" in line):
                print(line.replace('\n',''))
             if ("will be created" in line):
                print(line.replace('\n',''))
             if ("must be replaced" in line):
                print(line.replace('\n',''))
                lint=lines[(lines.index(line)):(len(lines))]
                lin=lint[0:(lint.index('\n'))]
                for l in lin:
                    if ("forces replacement" in l):
                        print(l.replace('\n',''))
                        print(lin[(lin.index(l))+1])
             if ("will be destroyed" in line):
                print(line.replace('\n',''))
             if ("Hit multiple errors" in line):
                 lint=lines[(lines.index(line)):(len(lines))]
                 for l in lint:
                     print(l.replace('\n',''))
                 print(bcolors.FAIL +" COULDNT PROCESS"+ bcolors.ENDC)
                 failedloglist.append(path)
                 continue
             if ("Unable to determine underlying exit code" in line):
                 lint=lines[(lines.index(line)):(len(lines))]
                 for l in lint:
                     print(l.replace('\n',''))
                 print(bcolors.FAIL +" COULDNT PROCESS"+ bcolors.ENDC)
                 failedloglist.append(path)
                 continue


def mr_changes():
    git_url="https://gitlab.com"
#     if len(sys.argv) > 1:
#         git_url = sys.argv[1]
    #os.mkdir("logs")
    logsFolder=pathlib.Path("logs").absolute().as_posix()
    idProject=os.environ.get('CI_PROJECT_ID')
    idCommit=os.environ.get('CI_COMMIT_SHA')
    gitlab_token=os.environ.get('gitlab_token')
    ci_commit_title=os.environ.get('CI_COMMIT_TITLE')

    gl = gitlab.Gitlab(git_url,private_token = gitlab_token)
    project = gl.projects.get(idProject)
    commit = project.commits.get(idCommit)
    diff = commit.diff()
    folderList=[]
    if (len(diff)==0):
        if not isdir(pathlib.Path(ci_commit_title).absolute().as_posix()):
            print(bcolors.FAIL+ci_commit_title +" is not valid path"+ bcolors.ENDC)
        else:
            ci_commit_titlePath=pathlib.Path(ci_commit_title).absolute().as_posix()
            printLogs=True
            printlog("plan",pathList ,logsFolder ,printLogs)
    else:
        for change in diff:
            newPath=change['new_path']
            if not ("live/") in newPath:
                print(pathlib.Path(newPath).absolute().as_posix()+bcolors.WARNING +" OUT of SCOPE"+ bcolors.ENDC)
            else:
                pathh=pathlib.Path(newPath).parent.absolute().as_posix()
                folderList.append(pathh)

    mylist = list(dict.fromkeys(folderList))
    TG_OUTPUT_LIMIT =3
    if os.environ.get("TG_OUTPUT_LIMIT")!=3 and os.environ.get("TG_OUTPUT_LIMIT")!=None :
        TG_OUTPUT_LIMIT = os.environ.get("TG_OUTPUT_LIMIT")
    printLogs=False
    if len(mylist)<=int(TG_OUTPUT_LIMIT):
        printLogs=True
    for path in mylist:

        if(isdir(path)):
            getAllFolder(path)

    printlog("plan" ,pathList ,logsFolder,printLogs )

    if failedloglist:
        for message in failedloglist:
            logfileName=message.split("live/")[1].replace("/","_")
            os.chdir(failedlogsFolder)
            shutil.move(logsFolder+"/"+logfileName+".log", "failed_"+logfileName+".log")
        sys.exit(1)
