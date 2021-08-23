import sys, os
from os.path import expanduser


TEMP_CACHE_FOLDER = os.path.join(expanduser("~"),".awsee","tmp")

def printPy(message: str, end: str=None):
    readyMsg = str(message)
    if end:
       print(readyMsg, file=sys.stderr, end=end)
    else:
       print(readyMsg, file=sys.stderr)

def printOut(message: str):
    readyMsg = str(message)
    print(readyMsg)
    
