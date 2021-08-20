import os
import sys
import time
import random

from py3toolbox import constants  as con


def get_mimetype(type=None, localname=None) :
  assert type is not None or localname is not None,  "type and localname, supply at least one parameter"
  
  if type is None: 
    type = localname.split(".")[-1]
  
  
  if type not in con.MIME_TYPES :
    type = "unknown"
  
  
  return con.MIME_TYPES[type]
    


def get_uid(case='L', digits=8):
  if case=='L' :
    alphabet = 'abcdefghijklmnopqrstuvwxyz0123456789'
  elif case == 'U':
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
  else:
    alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
  return ''.join(random.choices(alphabet, k=8))
    
  
if __name__ == "__main__":
  print (get_mimetype(type="folder"))
  print (get_mimetype(localname="r:/cow.png"))
  print (get_mimetype())
  