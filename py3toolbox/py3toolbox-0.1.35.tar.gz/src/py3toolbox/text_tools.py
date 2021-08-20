import os
import re
 
def re_search (re_pattern , text) :
  m = re.search(re_pattern, text)
  if m :  return m.groups
  return None

  
def re_findall (re_pattern , text) :
  m = re.findall(re_pattern, text)
  return m

def re_sub(re_pattern , text):
  return re.sub(re_pattern, text)




  
  
if __name__ == "__main__":
  str1 = 'product/900/162-11292V02G01'
  a = re_search('([^\/]*)$',str1)
  print (a(0)[0])
  #b = re_findall ('yaw=(\-*\d+\.\d*),pitch=(\-*\d+\.\d*),roll=(\-*\d+\.\d*)', 'MPU_1,yaw=-29.47,pitch=-7.54,roll=0.91')
  b = re_findall ('ENC\((.*)\)', 'truststore.password=EaNC(/ndgPwyPzRc56sv7r0BkSbGip76SN7GVhQqeyOzmQ+Y=)')
  print (b)
  
  pass  