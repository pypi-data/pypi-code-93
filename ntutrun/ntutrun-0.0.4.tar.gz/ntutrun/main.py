from robot.parsing.model import TestCaseFile, TestData, ResourceFile, TestDataDirectory
from robot.api import TestSuiteBuilder, TestSuite, ExecutionResult
from robot.result.executionresult import CombinedResult
from robot.result.model import TestSuite
from robot.run import RobotFramework
from robot import run_cli
from ntutrun.tree import Node
from ntutrun.FindVisitor import *
from ntutrun.TestCaseBuilder import *
from ntutrun.ResourceBuilder import *
from ntutrun.GitDifferent import *
from ntutrun.PythonResourceFile import *
from ntutrun.ReportResultVisitor import *
from os import path
import sys, codecs

def write_file(fileName, testCaseName, time):
    """write_file.

    Write test case and run time in .txt file 

    Args:
        fileName    : txt file name
        testCaseName: txt file path
        time        : test case run time 

    Returns:
        Non

    Raises:
        Non
    """
    out = open(fileName,"a")
    out.write(str(testCaseName)+"    "+str(time)+"\n")
    out.flush()

def check_tests(result, txt=None, outpath=None):
    """check_tests.

    Record test case and run time in .txt file 

    Args:
        result : run test case report out.xml file
        txt    : txt file path
        outpath: output path to save path

    Returns:
        Non

    Raises:
        Non
    """
    x=ReportResultVisitor()
    result.visit(x)
    if txt != None:
        for key, value in x.get_test_case_time().items():
            flag = 0
            for j in txt.keys():
                if key!=j:
                    pass
                else:
                    flag = 1
            if flag ==0:
                write_file(outpath,key,value)
    else:
        for key, value in x.get_test_case_time().items():
            write_file(outpath, key,value)

def check_test_status(result):
    """check_test_status.

    Check test case is fail or pass.

    Args:
        result : run test case report out.xml file

    Returns:
        test case status

    Raises:
        Non
    """
    x=ReportResultVisitor()
    result.visit(x)
    return x.get_test_case_status()

def convert_millis(millis):
    """convert_millis.

    Convert millis second to time. 

    Args:
        millis : millis second number

    Returns:
        hours
        minutes
        seconds

    Raises:
        Non
    """
    millis = int(millis)
    seconds=(millis/1000)%60
    seconds = int(seconds)
    minutes=(millis/(1000*60))%60
    minutes = int(minutes)
    hours=(millis/(1000*60*60))%24
    return (hours, minutes, seconds)

def main(ProjectPath, runUnderPath, userXmlFileXpath, precommitId, cmpcommitId, commandOPt, autoRun, outpath):
    fileNamePath=ProjectPath
    source_path = TestData(source=fileNamePath)
    allTestCases = TestCaseBuilder()
    allResourceFile = ResourceBuilder()
    testcases=allTestCases.build(source_path)
    allResourceFile.build(source_path)
    qq = FindVisitor(testcases)
    retval = os.getcwd()
    runtestcases=[]
    git=GitDifferent(fileNamePath)
    if precommitId != None and cmpcommitId == None:
        gitDiffInfo = git.getdifferent(precommitId)
    elif precommitId != None and cmpcommitId != None:
        gitDiffInfo = git.getdifferent(precommitId,cmpcommitId)
    else:
        gitDiffInfo = git.getdifferent()

    for diffkeywords in gitDiffInfo:
        affectTestCases=qq.showResult(allResourceFile.build(source_path), diffkeywords)
        # print("affectTestCase=",affectTestCases)
        for affectTestCase in affectTestCases:
            runtestcases.append(affectTestCase)
    userXmlFile=[]
    txt_path = retval+"/allTestCaseTime.txt"
    # print("txt_path",txt_path)

    # 如果使用者有提供XML檔案時
    # if userXmlFileXpath != None:
    #     userXmlFile.append(ExecutionResult(userXmlFileXpath))
    #     Combined=CombinedResult(userXmlFile)
    #     check_tests(Combined, outpath=txt_path)

    totalTime=0
    txt={}
    flag=0
    for runtestcase in set(runtestcases):
        # print(runtestcase)
        with codecs.open(txt_path, "r", 'utf-8') as lines: 
            for line in lines:
                txt[str(line.split("    ")[0])]=int(line.split("    ")[1])
                if str(line.split("    ")[0]) == str(runtestcase.name):
                    totalTime=totalTime+int(line.split("    ")[1])
                    flag=1
                    break
                else:
                    flag=0
        if flag==1:
            continue
    if flag == 1:
        print("===================================================\n")
        hours, minutes, seconds=convert_millis(totalTime)
        print ("Estimated total time to run dependent test cases is "+"%d時:%d分:%d秒" % (hours, minutes, seconds))
        print("===================================================\n")

    x=fileNamePath
    # x=fileNamePath+'\\RobotTests'
    # +'/'+runUnderPath
    os.chdir(x)
    # listener=os.path.abspath("./dctlib/listeners/no_rush.py")
    # print(listener)
    retval = os.getcwd()
    runtestcasesToPath=[]
    allXmlFiles=[]
    aaa=[]
    for runtestcase in set(runtestcases):
        # print("runtestcase.source=",runtestcase.source)
        if(type(runtestcase) == TestCaseFile):
            print("123456")
        else:
            runtestcasesToPath.append(runtestcase.name)
            aaa.append(runtestcase.source)
    # print(runtestcasesToPath)
    #     if you are run 
    option=[]
    # option.append("--variable")
    # option.append("dcTrackURL:https://140.124.181.118")
    # option.append("--listener")
    # option.append(listener)
    for i in runtestcasesToPath:
        option.append("--test")
        option.append(i)
        # option.append(*i)
    if commandOPt != None:
        for opt in commandOPt.split():
            option.append(opt)
        # option.append("./")
        # option.append("-P")
        # option.append("./Project AT test")
        if autoRun == "True":
            if runtestcasesToPath != []:
                run_cli([*option,*set(aaa)], exit=False)
                # print("outpath+/output.xml=",outpath+'/output.xml')
                allXmlFiles.append(ExecutionResult(outpath+'/output.xml'))
                Combined=CombinedResult(allXmlFiles)
                check_tests(Combined,txt, txt_path)
                status = check_test_status(Combined)
                print("You are run %d test case：\n" %len(set(runtestcases)))
                print("===================================================\n")
                for runtestcase in set(runtestcases):
                    # print(runtestcase.name)
                    if status[runtestcase.name] != True:
                        print(runtestcase.name+"--------Unexpected Error")
                        print(status[runtestcase.name])
                        print("===================================================\n")
                    else:
                        print(runtestcase.name+"--------Test Case Pass")
                        print("===================================================\n")
                print("Test coverage is %.2f%%" %(len(set(runtestcases))/len(testcases)*100))
            else:
                print("No test case is affected\n")