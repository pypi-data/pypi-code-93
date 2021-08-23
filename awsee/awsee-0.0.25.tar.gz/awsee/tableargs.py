import os, sys
import re

class TableArgs:

    def __init__(self):
        self.sortCol            = "1"
        self.desc               = False
        self.tagsTemp           = {}
        self.showTags           = False
        self.verbose            = False
        self.excelFile          = False
        self.csvDrawIo          = False
        self.saveToFile         = False
        self.highlightValue     = None
        self.filterValue        = None
        self.commandArguments   = None

    def setArguments(self, _commandArguments):
        self.commandArguments = _commandArguments

        arguments = self.commandArguments.split(",")

        for arg in arguments:
            if "sort" in arg:
                self.sortCol = arg.replace("sort","")  
            if "desc" in arg:
                self.desc = True
            if "showtags" in arg:
                self.showTags = True
            if "excel" in arg:
                self.excelFile = True
            if "drawio" in arg:
                self.csvDrawIo = True
            if "verbose" in arg:
                self.verbose = True
            if "save" in arg:
                self.saveToFile = True            
            # Look for  tags:Enviroment=Production;Project=Ecommerce    
            #if ("tags" in arg or "tag" in arg) and arg != "showtags":
            if  arg.startswith("tag:") or arg.startswith("tags:"):
                tagsArg = arg.replace("tags","tag").replace("tag:","")
                if "#" in tagsArg:
                  for tag in tagsArg.split("#"):
                     tagName  = tag.split("=")[0]
                     tagValue = tag.split("=")[1]
                     self.tagsTemp[tagName] = self._cleanPipelineArguments(tagValue)
                else:
                     tagName  = tagsArg.split("=")[0]
                     tagValue = tagsArg.split("=")[1]
                     self.tagsTemp[tagName] = self._cleanPipelineArguments(tagValue)


        if "|" in self.commandArguments:
           pos        = self.commandArguments.find("|")
           complement = self.commandArguments[pos:].replace(" | ","").replace("| ","").replace(" |","")
           if complement.startswith("grep"):
              self.filterValue = complement.replace("grep","") 
           else:
              self.highlightValue = complement   
           
        
        #print("verbose:     " + str(self.verbose))
        #print("saveToFile:  " + str(self.saveToFile))
        #print("desc:        " + str(self.desc))
        #if self.highlightValue: print("highlightValue:  " + self.highlightValue)
        #if self.filterValue: print("filterValue:  " + self.filterValue)
        #sys.exit()

    def cleanPipelineArguments(self):
        return self._cleanPipelineArguments(self.commandArguments)

    def _cleanPipelineArguments(self, str):
        if "|" in str:
            return str[:str.find("|")].strip()
        else:    
            return str
