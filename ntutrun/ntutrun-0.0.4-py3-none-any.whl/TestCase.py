from robot.parsing.model import TestCaseFile
class TestCase():
    def __init__(self, _TestCaseFile):
        # self._path = _path
        self._testcasefile = _TestCaseFile

    def accept(self,visitor):
        visitor.visitTestCaseFile(self)
    



    # def find_usage_from_testCaseFile(self, targetKeyword):
    #     usages = []
    #     for kw in self._testcasefile.keyword_table:
    #         usages.extend(self.find_usage_from_keyword(targetKeyword, kw))
    #     for test in self._testcasefile.testcase_table:
    #         usages.extend(self.find_usage_from_testcase(targetKeyword, test))
    #     usages.extend(self.find_usage_from_settings(targetKeyword, self._testcasefile.setting_table))
    #     if usages != []:
    #         return self._testcasefile.name
    #     else:
    #         return -1