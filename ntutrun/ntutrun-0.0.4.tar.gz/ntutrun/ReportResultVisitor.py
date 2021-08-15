from robot.api import ExecutionResult, ResultVisitor

class ReportResultVisitor(ResultVisitor):
    def __init__(self):
        self._testCaseAndTime = {}
        self._testCaseStatus = {}
        self._ans=""

    def visit_test(self, test):
        self._testCaseAndTime[test.parent.name]=test.parent.elapsedtime
        self._testCaseStatus[test.parent.name]=test.parent.passed
        if self._testCaseStatus[test.parent.name] != True:
            self._testCaseStatus[test.parent.name]=test.message
    
    def get_test_case_time(self):
        return self._testCaseAndTime
    
    def get_test_case_status(self):
        return self._testCaseStatus