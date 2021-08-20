import json
#import .fs_tools as fs_tools

def getdicv(dic, key):
  for k,v in dic.items():
    if k == key:
      return v
  return None
  
  
if __name__ == "__main__": 
  a = {"a.b" : "123"}
  print (getdicv(a,"a.b"))
  pass