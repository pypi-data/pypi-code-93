import re
class PythonResourceFile():
    def __init__(self, path):
        self._path = path
        self._number=[]
        self._keywords=[]
        self._function=[]
        self._keywordsToFunction={}
        self._numToKeywords={}
        self.readFile()

    def readFile(self):
        with open(self._path, "r") as lines: 
            t=0
            for count, line in enumerate(lines, 1): 
                if line.replace(" ","").startswith("@keyword"):
                    match1=re.search("'[A-Za-z].+'", line)
                    match2=re.search('"[A-Za-z].+"', line)
                    if match1 :
                        self._number.append(count)
                        self._keywords.append(match1.group().replace("'",""))
                        t=count
                    elif match2:
                        self._number.append(count)
                        self._keywords.append(match2.group().replace('"',''))
                        t=count
                regexp = re.compile(r"(def)\s(?P<function>\w+)")
                for m in regexp.finditer(line):
                    if  t != 0:
                        self._function.append(m.group("function"))
                        t=0

    def getRowCount(self):
        for i in range(0,len(self._number)):
            self._numToKeywords[self._number[i]]=self._keywords[i]
        return self._numToKeywords
    
    def getkeyword(self):
        for i in range(0,len(self._keywords)):
            self._keywordsToFunction[self._keywords[i]]=self._function[i]
        return self._keywordsToFunction
