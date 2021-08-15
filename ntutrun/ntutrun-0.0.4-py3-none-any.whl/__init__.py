# import ntutrun.main
from ntutrun.main import *
# from main import *


# def exe(ProjectPath, runUnderPath=None, outpath=None, userXmlFileXpath=None, precommitId=None, cmpcommitId=None, commandOPt=None, autoRun=True):
#     main(ProjectPath, runUnderPath, outpath, userXmlFileXpath, precommitId, cmpcommitId,commandOPt, autoRun)
def exe(**opt):
    ProjectPath=None
    runUnderPath=None
    outpath=None
    userXmlFileXpath=None
    precommitId=None
    cmpcommitId=None
    commandOPt=None
    autoRun=True
    arg={}
    options=["ProjectPath", "runUnderPath", "outpath", "userXmlFileXpath", "preCommitId" ,"cmpCommitId", "commandOPt", "autoRun"]
    for i in options:
        for key,value in opt.items():
            if key==i:
                arg[key]=value
                break
            else:
                arg[i]=None

    main(ProjectPath=arg["ProjectPath"], runUnderPath=arg["runUnderPath"], userXmlFileXpath=arg["userXmlFileXpath"], precommitId=arg["preCommitId"], cmpcommitId=arg["cmpCommitId"],commandOPt=arg["commandOPt"], autoRun=arg["autoRun"], outpath=arg["outpath"])
