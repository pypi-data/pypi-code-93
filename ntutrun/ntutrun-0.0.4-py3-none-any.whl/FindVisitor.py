from robot.parsing.model import ForLoop
from  ntutrun.tree import Node
class FindVisitor():
    def __init__(self, testcasefile):
        self.testcasefile=testcasefile

    def find_usage_from_settings(self, targetKeyword, setting):
        return [setting for setting in [setting.suite_setup, setting.suite_teardown, setting.test_setup, setting.test_teardown] if self.upper_compare(targetKeyword, setting._data_as_list())]
    
    def find_usage_from_keyword(self, targetKeyword, sourceKeyword):
        source = [step for step in sourceKeyword.steps]
        source.append(sourceKeyword.teardown)
        for step in source:
            if isinstance(step, ForLoop):
                for k in step.steps:
                    source.append(k)
        return [step for step in source if self.upper_compare(targetKeyword, step.as_list())]
    
    def upper_compare(self, string, stringItems):
        return string.upper() in [item.upper() for item in stringItems]
    
    def find_usage_from_testcase(self, targetKeyword, testcase):
        source = [step for step in testcase.steps]
        source.extend([testcase.template,testcase.setup, testcase.teardown])
        for step in source:
            if isinstance(step, ForLoop):
                for k in step.steps:
                    source.append(k)
        return [setting for setting in source if self.upper_compare(targetKeyword, setting.as_list())]
    
    def visitTestCaseFile(self, _targetKeywordName, ans, root):
        for t in self.testcasefile:
            qq=Node(t.name+"【TestSuite】")
            usages = []
            a=[]
            k=[]
            q=[]
            for test in t.testcase_table:
                usages = []
                usages.extend(self.find_usage_from_testcase(_targetKeywordName, test))
                if usages != []:
                    f=0
                    for i in set(q):
                        if i == t.name:
                            f=1
                            break
                    q.append(t.name)
                    if f==0:
                        root.add_child(qq)
                        ans.append(test)
                        qq.add_child(Node(test.name+"【TestCase】"))
                    else:
                        ans.append(test)
                        qq.add_child(Node(test.name+"【TestCase】"))
                        
                self.visitTestCaseKeyword(_targetKeywordName,t,k,q,qq,root)

                for kk in set(k):
                    testCaseKeyword=Node(kk+"【TestSuiteKeyword】")
                    usages = []
                    usages.extend(self.find_usage_from_testcase(kk, test))
                    if usages != []:
                            qq.add_child(testCaseKeyword)
                            testSuite=Node(test.name+"【TestCase】")
                            ans.append(test)
                            testCaseKeyword.add_child(testSuite)

            usages = []
            usages.extend(self.find_usage_from_settings(_targetKeywordName, t.setting_table))
            if usages != []:
                f=0
                for i in set(q):
                    if i == t.name:
                        f=1
                        break
                q.append(t.name)
                if f==0:
                    root.add_child(qq)
                    for test in t.testcase_table:
                        testSuite=Node(test.name+"【TestCase】")
                        ans.append(test)
                        qq.add_child(testSuite)

    def visitTestCaseKeyword(self,_keyword,t,k,q,qq,root):
        for kw in t.keyword_table:
                usages = []
                usages.extend(self.find_usage_from_keyword(_keyword, kw))
                if usages != []:
                    f=0
                    for i in set(q):
                        if i == t.name:
                            f=1
                            break
                    q.append(t.name)
                    if f==0:
                        root.add_child(qq)
                    f=0
                    for i in set(k):
                        if i == kw.name:
                            f=1
                            break
                    if f==0:
                        k.append(kw.name)
                        self.visitTestCaseKeyword(kw.name,t,k,q,qq,root)
        
    

    def visitResourceFile(self, resources, _targetKeywordName, ans, root):
        no=[]
        for resource in set(resources):
            if resource.keyword_table:
                for keyword in resource.keyword_table:
                    keyword_usages = self.find_usage_from_keyword(_targetKeywordName, keyword)
                    rootChild = Node(keyword.name+"【DependentKeyword】")
                    f=0
                    for i in no:
                        if i == keyword.name:
                            f=1
                            continue
                    no.append(keyword.name)
                    if len(keyword_usages)>0 and f==0:
                        if keyword.name == _targetKeywordName:
                            continue
                        root.add_child(rootChild)
                        usages = []
                        usages.append({'keyword':keyword.name,'usages':keyword_usages})
                        if usages != []:
                            for usage in usages:
                                self.visitTestCaseFile(usage['keyword'], ans, rootChild)
                        self.visitResourceFile(resources, keyword.name, ans, rootChild)
    
    def showResult(self, resources,  _targetKeywordName):
        ans = []
        root=Node(_targetKeywordName+"【ModifyKeyword】")
        self.visitTestCaseFile(_targetKeywordName, ans, root)
        self.visitResourceFile(set(resources), _targetKeywordName, ans, root)
        root.visualize(line_space=1)
        return ans



