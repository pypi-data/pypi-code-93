# -*- coding: utf-8 -*-

"""UCF Library: Unisos Common Functions/Facilities -- A collection of common functions that are primarily used by ICMs.
"""

####+BEGINNOT: bx:dblock:global:file-insert-cond :cond "./iimMiniDist.el" :file "/libre/ByStar/InitialTemplates/software/plusOrg/dblock/inserts/iimMiniDist.py"
"""\
Part of ByStar Digital Ecosystem http://www.by-star.net.
This module's primary documentation is in  http://www.by-star.net/PLPC/180047

This Python module was developed in the 
    COMEEGA: Collaborative Org-Mode Enhanced Emacs Generalized Authorship
model and is intended to be maintained in that model. Reading and editing this module
is best done with emacs and org-mode. Do not edit unless you are familiar with dblock org-mode.
Do not modify anything within a "dblock" as they are meant to be overwritten.
"""

####+END:

"""
*  [[elisp:(org-cycle)][| ]]  Author        :: Author and Version Information [[elisp:(org-cycle)][| ]]
"""
"""
*  [[elisp:(org-cycle)][| *Module-INFO:* |]]
"""
####+BEGINNOT: bx:dblock:global:iim:name-py :style "fileName"
__libName__ = "ucf"
####+END:

####+BEGIN: bx:dblock:global:timestamp:version-py :style "date"
__version__ = "201712055744"
####+END:

__status__ = "Almost Production"
__credits__ = [""]

# NOTYET dblk-begin
iicmInfo = {
    'authors':         ["[[http://mohsen.1.banan.byname.net][Mohsen Banan]]"],
    'copyright':       "Copyright 2017, [[http://www.neda.com][Neda Communications, Inc.]]",
    'licenses':        ["[[https://www.gnu.org/licenses/agpl-3.0.en.html][Affero GPL]]", "Libre-Halaal Services License", "Neda Commercial License"],
    'maintainers':     ["[[http://mohsen.1.banan.byname.net][Mohsen Banan]]",],
    'contacts':        ["[[http://mohsen.1.banan.byname.net/contact]]",],
    'partOf':          ["[[http://www.by-star.net][Libre-Halaal ByStar Digital Ecosystem]]",]
}
# NOTYET dblk-end


"""
####+BEGIN: bx:dblock:global:file-insert-cond :cond "./blee.el" :file "/libre/ByStar/InitialTemplates/software/plusOrg/dblock/inserts/topControls.org"
*      ================
*  /Controls/ ::  [[elisp:(org-cycle)][| ]]  [[elisp:(show-all)][Show-All]]  [[elisp:(org-shifttab)][Overview]]  [[elisp:(progn (org-shifttab) (org-content))][Content]] | [[file:Panel.org][Panel]] | [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] | [[elisp:(bx:org:run-me)][Run]] | [[elisp:(bx:org:run-me-eml)][RunEml]] | [[elisp:(delete-other-windows)][(1)]] | [[elisp:(progn (save-buffer) (kill-buffer))][S&Q]]  [[elisp:(save-buffer)][Save]]  [[elisp:(kill-buffer)][Quit]] [[elisp:(org-cycle)][| ]]
** /Version Control/ ::  [[elisp:(call-interactively (quote cvs-update))][cvs-update]]  [[elisp:(vc-update)][vc-update]] | [[elisp:(bx:org:agenda:this-file-otherWin)][Agenda-List]]  [[elisp:(bx:org:todo:this-file-otherWin)][ToDo-List]] 

####+END:
"""

"""
####+BEGIN: bx:dblock:global:file-insert-cond :cond "./blee.el" :file "/libre/ByStar/InitialTemplates/software/plusOrg/dblock/inserts/pythonWb.org"
*  /Python Workbench/ ::  [[elisp:(org-cycle)][| ]]  [[elisp:(python-check (format "pyclbr %s" (bx:buf-fname))))][pyclbr]] || [[elisp:(python-check (format "pyflakes %s" (bx:buf-fname)))][pyflakes]] | [[elisp:(python-check (format "pychecker %s" (bx:buf-fname))))][pychecker (executes)]] | [[elisp:(python-check (format "pep8 %s" (bx:buf-fname))))][pep8]] | [[elisp:(python-check (format "flake8 %s" (bx:buf-fname))))][flake8]] | [[elisp:(python-check (format "pylint %s" (bx:buf-fname))))][pylint]]  [[elisp:(org-cycle)][| ]]

####+END:
"""

"""
*      ================
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(delete-other-windows)][(1)]] CONTENTS-LIST ################
*  [[elisp:(org-cycle)][| ]]  Notes         :: *[Current-Info:]* Status/Maintenance -- General TODO List [[elisp:(org-cycle)][| ]]
*  [[elisp:(org-cycle)][| ]]  Info          :: *[Info]* General TODO List [[elisp:(org-cycle)][| ]]
**     ============ Essential Features TODO
*** TODO General review and consolidation with ICM
*** TODO Convert all functions to dblocks
*** TODO Everything related to frame and stack can go into its own module called runt.
Som we'll have runt.funcName runt.funcDocStr runt.funcDepth etc.
"""


"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(delete-other-windows)][(1)]]      *Imports And Description -- describe()*
"""

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || =Imports=        ::  Imports [[elisp:(org-cycle)][| ]]
"""

import sys
import os
import inspect
import gc
from datetime import datetime

import glob

import ast

import collections

from contextlib import contextmanager

import importlib

"""
*  [[elisp:(org-cycle)][| ]]  /General/            :: *Common Utilities -- Constants, Variables* [[elisp:(org-cycle)][| ]]
"""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Class            ::  Constants    [[elisp:(org-cycle)][| ]]
"""

class Constants:
    """ Example Usage: kpiResolution = iim.Constants(); kpiResolution.Minutes_15 = 1
    """
    def __setattr__(self, attr, value):
        if hasattr(self, attr):
            raise ValueError('Attribute %s already has a value and so cannot be written to' % attr)

        self.__dict__[attr] = value
        
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Class            ::  Variables    [[elisp:(org-cycle)][| ]]
"""

class Variables:
    """ Example Usage: kpiResolution = iim.Variables(); kpiResolution.Minutes_15 = 1
    """
    def __setattr__(self, attr, value):
        self.__dict__[attr] = value

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  enum  -- To Be Obsoleted by Enum   [[elisp:(org-cycle)][| ]]
"""
def enum(*sequential, **named):
    """A way to provide the equivalent of Enumerated Types.

    Example Usage:
    IIM_ParamScope = enum('TargetParam', 'IimGeneralParam', 'IifSpecificParam')
    var = IIM_ParamScope.TargetParam
    if var == IIM_ParamScope.IimGeneralParam:
    """
    enums = dict(list(zip(sequential, list(range(len(sequential))))), **named)
    return type('Enum', (), enums)

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  Enum    [[elisp:(org-cycle)][| ]]
"""
def Enum(*sequential, **named):
    """A way to provide the equivalent of Enumerated Types.

    Example Usage:
    IIM_ParamScope = Enum('TargetParam', 'IimGeneralParam', 'IifSpecificParam')
    var = IIM_ParamScope.TargetParam
    if var == IIM_ParamScope.IimGeneralParam:
    """
    Enums = dict(list(zip(sequential, list(range(len(sequential))))), **named)
    return type('Enum', (), Enums)



"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  enumFromStrWhenValid    [[elisp:(org-cycle)][| ]]
"""
def enumFromStrWhenValid(
        enumTypeStr,
        enumValueStr,
):
    """Given a string, return the Enum's value if valid. Applies to current module because of exec.

Usage: Should be checked against None.  if .enumFromStrWhenValid() == None: badInput()
"""
    enumRes = None
    try:
        #print "{0}.{1}".format(enumTypeStr, enumValueStr)
        exec("enumRes = {0}.{1}".format(enumTypeStr, enumValueStr))            
    except AttributeError:
        #print enumValueStr
        return None
    else:
        #print  enumRes
        return enumRes


"""
*  [[elisp:(org-cycle)][| ]]  /General/            :: *Call Tracking (decorators)* [[elisp:(org-cycle)][| ]]
"""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  format_arg_value    [[elisp:(org-cycle)][| ]]
"""

def format_arg_value(arg_val):
    """ Return a string representing a (name, value) pair.

    >>> format_arg_value(('x', (1, 2, 3)))
    'x=(1, 2, 3)'
    """
    arg, val = arg_val
    return "%s=%r" % (arg, val)



"""
*  [[elisp:(org-cycle)][| ]]  /General/            :: *Frame Marking and Tracking -- stackFrameInfoGet(frameNu)* [[elisp:(org-cycle)][| ]]
"""
    
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  stackFrameFuncGet-- Eliminate    [[elisp:(org-cycle)][| ]]
"""

def stackFrameFuncGet(frameNu):
    """Perhaps get rid of this and do info.function in the caller.
    """
    try: frameNu = int(frameNu)
    except: pass

    callerframerecord = inspect.stack()[frameNu]      # 0 represents this line (current frame)
    # 1 represents line at caller
    frame = callerframerecord[0]
    info = inspect.getframeinfo(frame)
    return (info.function)

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  stackFrameInfoGet -- Returns a string not info -- Should be re-done.   [[elisp:(org-cycle)][| ]]
"""
def stackFrameInfoGet(frameNu):
    """ Returns A String --
    """
    try: frameNu = int(frameNu)
    except: pass

    callerframerecord = inspect.stack()[frameNu]      # 0 represents this line (current frame)
    # 1 represents line at caller
    frame = callerframerecord[0]
    info = inspect.getframeinfo(frame)
    # print info.filename                       # __FILE__     -> Test.py
    # print info.function                       # __FUNCTION__ -> Main
    # print info.lineno                         # __LINE__     -> 13

    return info.filename + ':' + str(info.lineno) + ':' + info.function + ':'

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  stackFrameDepth    [[elisp:(org-cycle)][| ]]
"""

def stackFrameDepth(frameNu):
    """ Returns depth of specified frame as an integer.

    Additionally creates top to that frame list. -- But UnUsed.
    """
    try: frameNu = int(frameNu)
    except: pass

    caller_list = []

    callerframerecord = inspect.stack()[frameNu]      # 0 represents this line (current frame)
    # 1 represents line at caller
    frame = callerframerecord[0]

    #this_frame = frame  # Save current frame.

    level = 0
    while frame.f_back:
        level = level + 1
        caller_list.append('{0}()'.format(frame.f_code.co_name))
        frame = frame.f_back

    #caller_line = this_frame.f_back.f_lineno
    #callers =  '/'.join(reversed(caller_list))
    #logging.info('Line {0} : {1}'.format(caller_line, callers))
    return level

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  stackFrameDocString    [[elisp:(org-cycle)][| ]]
"""

def stackFrameDocString(frameNu):
    """
    """
    try: frameNu = int(frameNu)
    except: pass

    callerframerecord = inspect.stack()[frameNu]      #
    # 1 represents line at caller
    frame = callerframerecord[0]
    info = inspect.getframeinfo(frame)

    func = FUNC_strToFunc( info.function )

    #print "Called from module", info.f_globals['__name__']
    #print( getattr(info.filename, info.function) )
    #print( inspect.getdoc(getattr(info.function)) )
    return inspect.getdoc( func )
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  stackFrameArgsGet    [[elisp:(org-cycle)][| ]]
"""

def stackFrameArgsGet(frameNu):
    """
    """
    try: frameNu = int(frameNu)
    except: pass

    callerframerecord = inspect.stack()[frameNu]      #
    # 1 represents line at caller
    frame = callerframerecord[0]
    info = inspect.getframeinfo(frame)

    fn = FUNC_strToFunc( info.function )

    # Unpack function's arg count, arg names, arg defaults
    code = fn.__code__
    argcount = code.co_argcount
    
    argnames = code.co_varnames[:argcount]
    fn_defaults = fn.__defaults__ or list()
    argdefs = dict(list(zip(argnames[-len(fn_defaults):], fn_defaults)))
    #TM_here( info.function + ' -- '+ str(argcount) + str(argnames) + str(fn_defaults) + str(argdefs) )

    return argdefs



"""
*  [[elisp:(org-cycle)][| ]]  /Chunking/           :: *chunks(l, n) -- chunksNuOf(l, n)*    [[elisp:(org-cycle)][| ]]
"""
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  chunks    [[elisp:(org-cycle)][| ]]
"""

def chunks(l, n):
    """Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i:i+n]

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  chunksNuOf    [[elisp:(org-cycle)][| ]]
"""

def chunksNuOf(l, n):
    """Report NuOfChunks of  n-sized chunks from l."""
    listLength = len(l)
    remainder = listLength % n
    if remainder == 0:
        return listLength / n
    else: 
        return listLength / n + 1


"""
*  [[elisp:(org-cycle)][| ]]  /IIM Lib/            :: *percentage, runOnceOnly, setAdjust*  [[elisp:(org-cycle)][| ]]
"""

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  percentage    [[elisp:(org-cycle)][| ]]
"""
def percentage(part, whole):
  return 100 * float(part)/float(whole)

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  runOnceOnly    [[elisp:(org-cycle)][| ]]
"""
def runOnceOnly(f):
    """Meant to be used as a decorator or manually to ensure that we run f only once

@run_once
def my_function(foo, bar):
    return foo+bar

Now my_function will only run once. Other calls to it will return
None. Just add an else clause to the if if you want it to return
something else. From your example, it doesn't need to return anything
ever.

If you don't control the creation of the function, or the function
needs to be used normally in other contexts, you can just apply the
decorator manually as well.

action = run_once(my_function)
while 1:
    if predicate:
        action()

This will leave my_function available for other uses.

Finally, if you need to only run it once twice, then you can just do

action = run_once(my_function)
action() # run once the first time

action.has_run = False
action() # run once the second time
    """
    def wrapper(*args, **kwargs):
        if not wrapper.retVal:
            retVal = f(*args, **kwargs)
            wrapper.retVal = retVal
            return retVal
        else:
            return wrapper.retVal
    wrapper.retVal = None
    return wrapper


    # From the web before my imporvements
    #
    # def wrapper(*args, **kwargs):
    #     if not wrapper.has_run:
    #         wrapper.has_run = True
    #         return f(*args, **kwargs)
    # wrapper.has_run = False
    # return wrapper


def runOnceOnlyReturnFirstInvokation(f):
    """
    """
    def wrapper(*args, **kwargs):
        if not wrapper.retVal:
            retVal = f(*args, **kwargs)
            wrapper.retVal = retVal
            return retVal
        else:
            return wrapper.retVal
    wrapper.retVal = None
    return wrapper


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  iim_XmultiKeyDictList    [[elisp:(org-cycle)][| ]]
"""
#@subjectToTracking(fnLoc=True, fnEntry=False, fnExit=True)
def iim_XmultiKeyDictList(
        inList,
        multiKey,
):
    """Given a list, return a dictionary with repeated multiKey: list-element"""
    multiKeyDict = dict()
    for elem in inList:
        multiKeyDict[multiKey].append(elem)
    return multiKeyDict


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  setAdjustInfo    [[elisp:(org-cycle)][| ]]
"""
#@subjectToTracking(fnLoc=True, fnEntry=False, fnExit=True)
def setAdjustInfo(
        end,
        current
):
    """ A Set Operation which operates on two sets and Returns two set: deltasAdd, deltasRemove 
Such that current+deltasAdd-deltasRemove = end
    """
    if end != current:
        deltasAdd = end.difference(current)
        deltasRemove = current.difference(end) 
        return deltasAdd, deltasRemove
    else:
        return set(), set()
    



"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  perhapsInvokeHook    [[elisp:(org-cycle)][| ]]
"""
def perhapsInvokeHook(
        funcName,
        astFuncsDict,
):
    """Perhaps invoke funcName, if it exists in astFuncsDict.

NOTYET, Could be done more generally later.
"""
    try:
        func = astFuncsDict[funcName]
    except KeyError:
        return None
    else:
        return func()


"""
*  [[elisp:(org-cycle)][| ]]  /AST_/               :: *AST_ -- Abstract Syntax Tree Analysis* [[elisp:(org-cycle)][| ]]
"""

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  ast_topLevelClasses    [[elisp:(org-cycle)][| ]]
"""
def ast_topLevelClasses(body):
    classesList=list()
    for eachClass in body:
        if isinstance(eachClass, ast.ClassDef):
            classesList.append(eachClass)
    return (classesList)
    # Generator model is not re-usable -- Avoided by choice
    #return (f for f in body if isinstance(f, ast.FunctionDef))

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  ast_topLevelFunctions    [[elisp:(org-cycle)][| ]]
"""
def ast_topLevelFunctions(body):
    funcsList=list()
    for func in body:
        if isinstance(func, ast.FunctionDef):
            funcsList.append(func)
    return (funcsList)
    # Generator model is not re-usable
    #return (f for f in body if isinstance(f, ast.FunctionDef))
    
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  ast_parseFile    [[elisp:(org-cycle)][| ]]
"""
def ast_parseFile(filename):
    with open(filename, "rt") as thisFile:
        return ast.parse(thisFile.read(), filename=filename)
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  ast_topLevelFunctionsInFile    [[elisp:(org-cycle)][| ]]
"""
def ast_topLevelFunctionsInFile(filename):
    tree = ast_parseFile(filename)
    return(
        ast_topLevelFunctions(tree.body)   
    )

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  ast_topLevelClassesInFile    [[elisp:(org-cycle)][| ]]
"""
def ast_topLevelClassesInFile(filename):
    tree = ast_parseFile(filename)
    return(
        ast_topLevelClasses(tree.body)   
    )

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  ast_topLevelClassNamesInFile    [[elisp:(org-cycle)][| ]]
"""
def ast_topLevelClassNamesInFile(filename):
    classes = ast_topLevelClassesInFile(filename)
    classNames = list()
    for each in classes:
        classNames.append(each.name)
    return classNames

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  ast_topLevelFunctionNamesInFile    [[elisp:(org-cycle)][| ]]
"""
def ast_topLevelFunctionNamesInFile(filename):
    """Not using generators by choice."""
    funcs = ast_topLevelFunctionsInFile(filename)
    funcNames = list()
    for each in funcs:
        funcNames.append(each.name)
    return funcNames

        
"""
*  [[elisp:(org-cycle)][| ]]  /General-Misc/       :: *Common-Misc Utilities -- FUNC_* [[elisp:(org-cycle)][| ]]
"""

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  FUNC_strToFunc    [[elisp:(org-cycle)][| ]]
"""
def FUNC_strToFunc(astr):
    """Given a String, return the callable with that name.

    BUG: if astr is that of a module, just __import__ does not work.
    """
    module, _, function = astr.rpartition('.')
    if module:
        __import__(module)
        mod = sys.modules[module]
        return getattr(mod, function)
    else:
        #mod = sys.modules['__main__']  # or whatever's the "default module"
        #return globals()[function]
        mod = __import__('__main__')

        print(function)
        #return locals()[function]
        return getattr(mod, function)

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  FUNC_currentGet    [[elisp:(org-cycle)][| ]]
"""

def FUNC_currentGet(frameNu=1):
    """Returns the object for current frame.
This is used by a function when that function is running.
It returns a pointer to the running function.
Further details of the function can then be obtained by FUNC_currentXxx.

If it is directly called by the running function, then frameNu is x.
If it is called by an intermediate function such as EH_problem, then frameNu is x+1.
    
    BUG: does not work outside of the main module with PY2. Needs PY3 testing.
    """

    frame,filename,line_number,function_name,lines,index = inspect.stack()[frameNu]
    # print(frame,filename,line_number,function_name,lines,index)

    modName = "." + inspect.getmodulename(filename)

    try:
        mod = importlib.import_module(modName, package="bisos")
    except ModuleNotFoundError:
        mod=None
    if mod:
        func = getattr(mod, function_name, None)
        if func:
            return func

    try:
        mod = importlib.import_module(modName, package="unisos")
    except ModuleNotFoundError:
        mod=None
    if mod:
        func = getattr(mod, function_name, None)
        if func:
            return func


    print("UCF-Problem: Missing mod and func. " + modName)
    return None


def FUNC_current():
    """ When called as iicm.FUNC_current() frameNu=2"""
    return FUNC_currentGet(frameNu=2)

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  Func_currentNameGet    [[elisp:(org-cycle)][| ]]
"""

def Func_currentNameGet():
    """Returns the name of the object for current frame which would be this function's name.

    BUG: does not work outside of the main module.
    """

    thisFunc = FUNC_currentGet(frameNu=2)
    return thisFunc.__name__


def FUNC_currentNameGet():
    """Returns the name of the object for current frame which would be this function's name.

    BUG: does not work outside of the main module.
    """

    thisFunc = FUNC_currentGet(frameNu=2)
    return thisFunc.__name__

def FUNC_currentName():
    """Returns the name of the object for current frame which would be this function's name.

    BUG: does not work outside of the main module.
    """

    thisFunc = FUNC_currentGet(frameNu=2)
    return thisFunc.__name__


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  FUNC_argsLength    [[elisp:(org-cycle)][| ]]
"""

def FUNC_argsLength(fn, *v, **k):
    """Returns the length of arguments, given a function object.
** TODO ============    Returns length of string '()' not the actual args.
    """

    # PY2.7  #NOTYET IMPORTANT
    #if not fn:
    #    return


    # Unpack function's arg count, arg names, arg defaults
    code = fn.__code__
    argcount = code.co_argcount

    argnames = code.co_varnames[:argcount]
    fn_defaults = fn.__defaults__ or list()
    argdefs = dict(list(zip(argnames[-len(fn_defaults):], fn_defaults)))

    positional = list(map(format_arg_value, list(zip(argnames, v))))
    defaulted = [format_arg_value((a, argdefs[a]))
       for a in argnames[len(v):] if a not in k]
    nameless = list(map(repr, v[argcount:]))
    keyword = list(map(format_arg_value, list(k.items())))
    args = positional + defaulted + nameless + keyword

    return   len(args[0])

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  TIME_nowTag    [[elisp:(org-cycle)][| ]]
"""

def TIME_nowTag():
    INTERVAL_TIMESTAMP_FORMAT = "%Y%m%d%H%M%S"
    startTime = datetime.strftime(datetime.now(), INTERVAL_TIMESTAMP_FORMAT)
    return startTime
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  STR_insertMultiples    [[elisp:(org-cycle)][| ]]
"""

def STR_indentMultiples(multiple=1, unit="  "): STR_insertMultiples(multiple=1, unit="  ") # obsoleted


def STR_insertMultiples(
                multiple=1,
                unit="  ",
):
    """Return multiples of unit."""
    retVal = ""
    count = 0
    while count < multiple:
        retVal = retVal + unit
        count = count + 1
    return retVal

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  str_endsWith    [[elisp:(org-cycle)][| ]]
"""
def str_endsWith(inStr, endStr):
    """Verify that inStr includes endStr. """
    if inStr.find(endStr) < 0:
        return False
    return True


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  str_joinedArgs    [[elisp:(org-cycle)][| ]]
"""
def str_joinedArgs(argsList):
    joinedArgs = ""
    for each in argsList:
        if " " in each:
            joinedArgs += ''' "{each}"'''.format(each=each)
        else:
            joinedArgs += """ {each}""".format(each=each)
    return joinedArgs


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  STR_getFirstLine    [[elisp:(org-cycle)][| ]]
"""

def LINES_getFirstLine(lines): return STR_getFirstLine(lines)  # obsoleted
def STR_getFirstLine(lines): return lines.splitlines()[0]

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  listPrintItems    [[elisp:(org-cycle)][| ]]
"""
def listPrintItems(inList):
    for each in inList:
        print(each)

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  oDict    [[elisp:(org-cycle)][| ]]
"""
def oDict(**kwargs):
    """Return An OrderedDict. -- Does not work because kwargs are not ordered till Python 3.6."""
    d = collections.OrderedDict()
    for key in kwargs:
        d[key] = kwargs[key]
    return d

"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  stdout_redirector    [[elisp:(org-cycle)][| ]]
"""
@contextmanager
def stdout_redirector(stream):
    """ Example Usage:

        #f = io.StringIO()
        #f = io.BytesIO()

        with open(impressiveInfoPath, 'w') as f:
            with stdout_redirector(f):
                dispositionToImpressiveInfoPurposedStdout().cmnd(
                    interactive=False,
                    dispositionBase=dispositionBase,
                    argsList=effectiveArgsList,
                )

        #print('Got stdout: "{0}"'.format(f.getvalue()))
"""
    old_stdout = sys.stdout
    sys.stdout = stream
    try:
        yield
    finally:
        sys.stdout = old_stdout


"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func             ::  DIR_ensure    [[elisp:(org-cycle)][| ]]
"""
def DIR_ensure(file_path):
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        try: os.makedirs(directory, 0o777 )
        except OSError: pass

####+BEGIN: bx:icm:python:func :funcName "DIR_ensureDir" :funcType "void" :retType "bool" :deco "" :argsList "dirPath"
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func-void      :: /DIR_ensureDir/ retType=bool argsList=(dirPath)  [[elisp:(org-cycle)][| ]]
"""
def DIR_ensureDir(
    dirPath,
):
####+END:
    """ Ensure that specified directory exists."""
    try: 
        os.makedirs(dirPath)
    except OSError:
        if not os.path.isdir(dirPath):
            raise

####+BEGIN: bx:icm:python:func :funcName "DIR_ensureForFile" :funcType "void" :retType "bool" :deco "" :argsList "filePath"
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func-void      :: /DIR_ensureForFile/ retType=bool argsList=(filePath)  [[elisp:(org-cycle)][| ]]
"""
def DIR_ensureForFile(
    filePath,
):
####+END:
    dirPath = os.path.dirname(filePath)
    DIR_ensureDir(dirPath)
        

####+BEGIN: bx:icm:python:func :funcName "FN_latestInDir" :funcType "anyOrNone" :retType "bool" :deco "" :argsList "dirPath"
"""
*  [[elisp:(org-cycle)][| ]]  [[elisp:(org-show-subtree)][|=]] [[elisp:(show-children)][|V]] [[elisp:(org-tree-to-indirect-buffer)][|>]] [[elisp:(blee:ppmm:org-mode-toggle)][Nat]] [[elisp:(beginning-of-buffer)][Top]] [[elisp:(delete-other-windows)][(1)]] || Func-anyOrNone :: /FN_latestInDir/ retType=bool argsList=(dirPath)  [[elisp:(org-cycle)][| ]]
"""
def FN_latestInDir(
    dirPath,
):
####+END:
    list_of_files = glob.glob("{}/*".format(dirPath)) 
    latest_file = max(list_of_files, key=os.path.getctime)
    return latest_file
        


"""
*  [[elisp:(beginning-of-buffer)][Top]] ################ [[elisp:(delete-other-windows)][(1)]]      *End Of Editable Text*
"""

"""
*  [[elisp:(org-cycle)][| ]]  COMMON        :: /[dblock] -- End-Of-File Controls/ [[elisp:(org-cycle)][| ]]
"""

####+BEGIN: bx:dblock:global:file-insert-cond :cond "./blee.el" :file "/libre/ByStar/InitialTemplates/software/plusOrg/dblock/inserts/endOfFileControls.org"
#+STARTUP: showall

####+END:
