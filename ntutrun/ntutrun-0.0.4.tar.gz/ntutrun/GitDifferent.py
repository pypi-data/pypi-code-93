import os
import string
import re 
from git.diff import Diffable,DiffIndex
from git import Repo
import git
from ntutrun.PythonResourceFile import *

class GitDifferent:
    def __init__(self, _path):
        self.repo= Repo(_path)
        self.path=_path

    def getdifferent(self, commitID_1=None, commitID_2=None):
        fileNameAndkeywords={}
        keyword=[]
        path=''
        os.chdir(self.path)
        if commitID_1 != None and commitID_2 == None:
            diffSource = self.repo.git.diff("-U0", commitID_1)
        elif commitID_1 != None and commitID_2 != None:
            diffSource = self.repo.git.diff("-U0", commitID_1, commitID_2)
        else:
            diffSource = self.repo.git.diff("-U0")
        
        # self.repo.commit(self.repo.active_branch.name)
        # 取得變更資訊
        for q in diffSource.split("\n"):
            if q.startswith("+++") or q.startswith("---"):
                match=re.search("/[A-Za-z]+.*", q.replace('\\t',""))
                if match:
                    keyword=[]
                    path=(self.path+match.group()).replace('\t',"")
            if q.startswith("@@"):
                match1 = re.search("\+[0-9]+", q)
                if match1:
                    keyword.append(match1.group().replace('+',""))
                fileNameAndkeywords[path]=keyword
        # 建立表
        t={}
        regex = re.compile(r"[A-Z-a-z].*") 
        for key in fileNameAndkeywords.keys():
            root_keyword={}
            if((key.endswith(".py")) or (key.endswith(".robot")) or (key.endswith(".txt"))):
                with open(key, "r", encoding="utf-8") as lines: 
                    i=1
                    for line in lines: 
                        match = re.match(regex, line) 
                        if match: 
                            root_keyword[i]=match.group()
                        i=i+1
                t[key]=root_keyword
            else:
                continue

#        #取得變更行數 
        changeKeywords=[]
        for key, vlaue in fileNameAndkeywords.items():
            # key=FileName
            # Value=ChangeKeywordNum
            ans=0
            for v in vlaue:
                if key.endswith(".py") or key.endswith(".txt") or key.endswith(".robot"):
                    if str(key).endswith('.py'):
                        py=PythonResourceFile(str(key))
                        x=py.getRowCount()
                        if x == {} :
                            continue
                        min=100000
                        for j in x.keys():
                            if int(v)-j>=0 and int(v)-j<=min:
                                min=int(v)-j
                                ans=j
                        if x[ans] != None:
                            changeKeywords.append(x[ans])
                    else:
                        min=100000
                        for num in t[key].keys():
                            if int(v)-num>=0 and int(v)-num<=min:
                                min=int(v)-num
                                ans=num
                            
                        if t[key].get(ans) != None:
                            changeKeywords.append(t[key].get(ans))
                            
        return set(changeKeywords)