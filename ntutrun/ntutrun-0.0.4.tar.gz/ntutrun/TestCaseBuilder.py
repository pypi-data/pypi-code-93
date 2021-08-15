from os import path
from robot.parsing.model import ResourceFile ,TestCaseFile ,TestDataDirectory
from  ntutrun.Builder import *

class TestCaseBuilder(Builder):
    def list_all_suite(self, suite ,allTestCase):
        for child in suite.children:
            allTestCase.append(child)
            self.list_all_suite(child, allTestCase)

    def build(self,testDataDir):
        allTestCases = []
        self.list_all_suite(testDataDir,allTestCases)
        CommomKeyword = []
        for allTestCase in allTestCases:
            if not isinstance(allTestCase,TestDataDirectory):
                CommomKeyword.append(TestCaseFile(source=allTestCase.source).populate())
        return CommomKeyword
