import os
import sys
import re
import hashlib
import pathlib
import glob
import gzip
import codecs
import base64
import time


from shutil import copyfile,rmtree
from stat import * 
from py3toolbox.text_tools import re_findall


####################################################################################################

def rm_folder(folder_name, empty=False):
  """
  Remove/Delete Folder
  Usage :
    rm_folder(folder_name, empty=False):
      - empty = True  : empty the folder only, folder still remains
      - empty = False : Remove the entire folder with all sub folder and files.

  Sample :
    rm_folder("R:/temp1", empty=False)

  """
  if empty == False:
    rmtree(folder_name,ignore_errors=True)
  else:
    rmtree(folder_name,ignore_errors=True)
    mk_folder(folder_name=folder_name)

delete_folder = rm_folder
rm_dir        = rm_folder


####################################################################################################

def mk_folder(folder_name) :
  """
    Create New Folder(s)
    Usage : 
      mk_folder(folder_name) 
      - folder_name can be multiple layers, and all of them will be created.

    Sample:  
      mk_folder("r:/temp1/t1/t2/t3") 

  """
  if file_exists(folder_name) == False :
    os.makedirs(folder_name, exist_ok=True)

create_folder = mk_folder
make_folder   = mk_folder
make_dir      = mk_folder
####################################################################################################


def clean_folder(folder_name):
  """
    Clean/Empty Folder

    Usage : 
      clean_folder(folder_name) 
      - folder_name : full folder path

    Sample:  
      clean_folder("r:/temp1/t1/t2") 

  """
  mk_folder(folder_name)
  rm_folder(folder_name, empty=True)


####################################################################################################

def get_file_folder(file_path) :
  """
    Get folder path of given file full path
    Usage : 
      get_file_folder(file_path) 
      - file_path : is the full file path

    Sample:  
      get_file_folder("r:/temp1/t1/t2/t3/file1.txt") => r:/temp1/t1/t2/t3

  """  
  return os.path.dirname(file_path)


####################################################################################################


def get_file_name(file_path) :
  """
    Get file base name from given full path
    Usage : 
      get_file_name(file_path) 
      - file_path : is the full file path

    Sample:  
      get_file_name("r:/temp1/t1/t2/t3/file1.txt") => file1.txt

  """    
  return os.path.basename(file_path)


####################################################################################################

def parse_full_path (file_path):
  """
    Get file base name from given full path
    Usage : 
      get_file_name(file_path) 
      - file_path : is the full file path

    Sample:  
      parse_full_path("r:/temp1/t1/t2/t3/file1.txt") => ("r:/temp1/t1/t2/t3", "file1.txt")

  """      
  path = get_file_folder(file_path)
  name = get_file_name(file_path)
  return (path, name)


####################################################################################################





def file_exists(file_name):
  return os.path.exists(file_name)
exists = file_exists


####################################################################################################
  
def copy_file(src_file,dest_file):
  if file_exists(src_file) :  
    mk_folder(get_file_folder(dest_file))
    copyfile(src_file,dest_file)    





####################################################################################################  
def rm_file(file_name = None, folder = None, regex_pattern=None) :
  """
    Remove file(s), if file_name is list, then remove all of them.
    Remove file based on the regex pattern 
    
    Sample:
      rm_file(file_name = 'r:/temp/1.txt')                      ==> remove R:/temp/1.txt
      rm_file(file_name = ['r:/temp/1.txt', 'r:/temp/2.txt'] )  ==> remove R:/temp/1.txt and R:/temp/2.txt
      
      rm_file(folder = "R:/temp", regex_pattern='\d+\.txt' )    ==> remove R:/temp/{1,2,3...}.txt
      
  """
  
  # if only folder and regex_pattern provided
  if file_name is None and folder is not None and regex_pattern is not None:
    file_name = []
    for f in get_files(folder = folder, type='file'):
      if len(re_findall(regex_pattern, f)) > 0:
        file_name.append(f)
    
  # perform file delete 
  if type(file_name) is list:
    for f in file_name:
      if os.path.isfile(f): 
        os.remove(f)
  else:
    if os.path.isfile(file_name): 
      os.remove(file_name)

del_file = rm_file

####################################################################################################          
        
def write_file(file_name, text, mode='w', is_new = False):
  file_folder = get_file_folder(file_name)
  if file_exists(file_folder) == False: mk_folder(file_folder)
    
  if is_new == True: rm_file(file_name)
  with codecs.open(file_name, mode, 'utf8') as fh:
    fh.write(text)

####################################################################################################  


def write_log(file_name, text, is_new = False):
  write_file(file_name=file_name, text=text + "\n", mode='a', is_new=is_new)


####################################################################################################  


    
def read_file(file_name, return_type='str'):
  if return_type == 'str' :
    return codecs.open(file_name, 'r', 'utf8').read()
    
  if return_type == 'list' :
    return codecs.open(file_name, 'r', 'utf8' ).readlines() 


####################################################################################################

    
def get_md5(file_name) :  
  hasher = hashlib.md5()
  with open(file_name, 'rb') as fh:
    buf = fh.read()
    hasher.update(buf)
  return (hasher.hexdigest())

####################################################################################################



def get_md5_txt(text) :  
  return hashlib.md5(text.encode('utf-8')).hexdigest()


####################################################################################################

  
def is_file (file) :
  return os.path.isfile(file) 

def is_folder (file) :
  return os.path.isdir(file) 
  
def check_type(full_path):
  if file_exists(full_path) : 
    if is_file(full_path) : 
      return 'file'
    elif is_folder(full_path) :  
      return 'dir'
  else:
    return None
  
####################################################################################################  
  
  
def scan_fs_tree(folder, ext='', recursive=True, type='A'):
  
  for obj in os.scandir(folder):
    if obj.is_dir(follow_symlinks=False):
      if type.upper()=='A' or type.upper()=='ALL' or type.upper()=='D' or type.upper()=='DIR'  or type.upper()=='FOLDER':
        yield obj
      if recursive  == True: 
        yield from scan_fs_tree(folder=obj.path, ext=ext, recursive=recursive, type=type) 
    else:
      if type.upper()=='A' or type.upper()=='ALL' or type.upper()=='F' or type.upper()=='FILE':
        if ext == '':
          yield obj
        else:
          if obj.name.endswith(ext) :  yield obj
      pass

####################################################################################################


def gen_files(folder, ext='',  recursive=True, type='A'):
  for f in scan_fs_tree(folder=folder,  ext=ext, recursive=recursive, type=type):
    file_path = f.path
    if os.name == 'nt':
      file_path = file_path.replace('\\', '/')
    yield file_path
    
####################################################################################################
def get_files(folder, ext='', recursive=True, type='A') : 
  files = []
  for f in gen_files(folder=folder, ext = ext, recursive=recursive, type=type):
    files.append(f)
  return files

####################################################################################################

def get_file_info(file_name) :
  if file_exists(file_name):
    st = os.stat(file_name)
    return { "file_name": file_name, "size" : int(st[ST_SIZE]), "access_time" : st[ST_ATIME] }
  else:
    return None

####################################################################################################
# 
#   
def get_folder_info(folder, recursive=True ):
  """
    
  
  
  """
  
  total_size  = 0
  total_count = 0
  files = get_files(folder=folder, recursive=recursive)
  total_count = len(files)
  for f in files : 
    total_size += get_file_info(f)["size"]
  
  return (total_count, total_size)  

####################################################################################################

def do_zip(input_file=None,output_file=None,input_data=None, output="file"):
  """
  usage  : 
    zip compress input file or bytes string or string
    output: file  : save as file
            byte  : return bytes string
  
  examples:
    do_zip(input_file="c:/1.txt",output_file="c:/1.zip")
    do_zip(input_file="c:/1.txt",output="byte")

    do_zip(dest_file="c:/1.zip", input_data="test_string",output="file")
    do_zip(input_data="test_string",output="byte")

  """

  assert output == "file" or  output == "byte" , "Wrong output type : should be file or byte"

  # check input 
  if input_file is not None:
    with open(input_file, 'rb') as f_in: 
      input_data = f_in.read()
  elif input_data is not None:
    if type(input_data).__name__ == 'str' :
      input_data =  str.encode(input_data)


  compressed_bytes = gzip.compress(input_data, compresslevel=9)


  if output == "file":
    with open(output_file, 'wb') as f_out: 
      f_out.write(compressed_bytes)
    return output_file
  elif output == "byte":
    return  compressed_bytes

  pass


####################################################################################################

def do_unzip(input_file=None,output_file=None,input_data=None, output="file"):
  """
  usage  : 
    do_unzip decompress (unzip) input file or bytes string or string
    output: file  : save as file
            byte  : return bytes string
  
  examples:
    do_unzip(input_file="c:/1.zip",dest_file="c:/1.bin")
    do_unzip(input_file="c:/1.zip",output="byte")

    do_unzip(output_file="c:/1.zip", input_data="test_string",output="file")
    do_unzip(input_file="test_string",output="byte")

  """

  assert output == "file" or  output == "byte" , "Wring output type : should be file or byte"

  # check input 
  if input_file is not None:
    with open(input_file, 'rb') as f_in: 
      input_data = f_in.read()
  elif input_data is not None:
    if type(input_data).__name__ == 'str' :
      input_data =  str.encode(input_data)

  decompressed_bytes = gzip.decompress(input_data)

  if output == "file":
    with open(output_file, 'wb') as f_out: 
      f_out.write(decompressed_bytes)
    return output_file
  elif output == "byte":
    return  decompressed_bytes

  pass



"""
def unzip(gzfile) :
  fgz = gzip.GzipFile(gzfile, 'rb')
  binary_content = fgz.read()
  fgz.close()
  return binary_content
"""



####################################################################################################

def split_file(input_file, output_folder, volume_size=10):
  """
    Split file to multiple volumes by size 
    
    Sample:
      split_file(input_file='R:/Temp2/disk.bin', output_folder ='R:/Temp2', volume_size=1234)
      join_file(input_file='R:/Temp2/disk.bin',  output_folder ='R:/Temp1')
  
  """
  assert input_file is not None and output_folder is not None, "Error: input_file, output_folder are required."
  
  part_number = 0
  volume_size = volume_size * 1024 * 1024
  
  # cleanup volume files before creating new ones
  rm_file(folder = output_folder, regex_pattern = get_file_name(input_file) + '\.part_\d+')
  
  with open(input_file,"rb") as f:
    chunk = f.read(volume_size)
    while chunk:
      chunk_file = output_folder + '/' + get_file_name(input_file) + '.part_' + str(part_number).zfill(5)
      with open(chunk_file , "wb" ) as chunk_fh:
        chunk_fh.write(chunk)
        chunk_fh.flush()
      part_number += 1
      chunk = f.read(volume_size)
    
  return

####################################################################################################


def join_file(input_file, output_folder , volume_size=None):
  """
    Join files from multiple volumes 
    
    Sample:
      split_file(input_file='R:/Temp2/disk.bin', output_folder ='R:/Temp2', volume_size=1234)
      join_file(input_file='R:/Temp2/disk.bin',  output_folder ='R:/Temp1')
  
  """
  
  assert input_file is not None  or  output_file is not  None, "input_file, output_file are required"
  
  input_folder, file_name = parse_full_path(input_file)
  
  file_list = []
  for f in get_files(folder=input_folder, type='file') :
    if file_name + '.part_' in f:
      file_list.append(f)
  file_list.sort()
  
  output_file = os.path.join(output_folder , file_name)
  
  # cleanup volume files before creating new ones
  rm_file(file_name = os.path.join(output_folder,output_file))
  
  for f in file_list:
    with open(f,"rb") as fh:
      chunk = fh.read()
      with open(output_file , "ab" ) as  output_fh:
        output_fh.write(chunk)
        output_fh.flush()

  print (file_list)
  return
  
####################################################################################################
def compare_files(source, target):
  """
    Compare two files by MD5
    
    Sample:
      compare_files('R:/Temp1/1.txt', 'R:/Temp1/2.txt') 
      - Returns True  : two files identical
      - Returns False : two files different
      
  """
  
  return (get_md5(source) == get_md5(target))


####################################################################################################

def base64_encode(input_file=None,output_file=None,input_data=None, output="file"):
  """
  usage  : 
    base64 encode input file or bytes string or string
    output: file  : save as file
            text  : return bytes string
  
  examples:
    base64_encode(input_file="c:/1.txt",output_file="c:/1.zip")
    base64_encode(input_file="c:/1.txt",output="text")

    base64_encode(dest_file="c:/1.zip", input_data="test_string",output="file")
    base64_encode(input_data="test_string",output="text")

  """
  assert output == "file" or  output == "text" , "Wrong output type : should be file or text"
  
  # check input 
  if input_file is not None:
    with open(input_file, 'rb') as f_in: 
      input_data = f_in.read()
  elif input_data is not None:
    if type(input_data).__name__ == 'str' :
      input_data =  str.encode(input_data)

  encoded_bytes = base64.b64encode(input_data)
 
  if output == "file":
    with open(output_file, 'wb') as f_out: 
      f_out.write(encoded_bytes)
    return output_file
  elif output == "text":
    return  encoded_bytes.decode() 


#################################################################################################### 

def base64_decode(input_file=None,output_file=None,input_data=None, output="file"):
  """
  usage  : 
    base64 decode input file or bytes string or string
    output: file  : save as file
            byte  : return bytes string
  
  examples:
    base64_decode(input_file="c:/1.txt",output_file="c:/1.zip")
    base64_decode(input_file="c:/1.txt",output="byte")

    base64_decode(dest_file="c:/1.zip", input_data="test_string",output="file")
    base64_decode(input_data="test_string",output="byte")

  """
  
  assert output == "file" or  output == "byte" , "Wring output type : should be file or byte"
  input_text = None

  # check input 
  if input_file is not None:
    with open(input_file, 'rb') as f_in: 
      input_data = f_in.read()

  # convert to ascii
  if type(input_data).__name__ != 'str' :
    input_text =  input_data.decode()
  else:
    input_text = input_data

  assert input_text is not None, "Error of reading input"

  decoded_bytes = base64.b64decode(input_text)
 
  if output == "file":
    with open(output_file, 'wb') as f_out: 
      f_out.write(decoded_bytes)
    return output_file
  elif output == "byte":
    return  decoded_bytes

  pass



####################################################################################################

def reverse_str(text) :
  """
    return reversed the text str, can be used for encryption
    
  """
  reversed_txt = text[::-1]
  return reversed_txt


####################################################################################################

def encrypt(input_file=None,output_file=None):
  """
    encrypt file (has to be coupled with decrypt function)
    no password required.
    
  """
  zip_data = do_zip(input_file=input_file,output="byte")
  b64_data = base64_encode(input_data=zip_data,output="text")
  r_b64_data = reverse_str(b64_data)
  with open(output_file, 'wt') as f_out: 
    f_out.write(r_b64_data)
    f_out.flush()
  pass

####################################################################################################
  
def decrypt(input_file=None,output_file=None):
  """
    decrypt file (has to be coupled with encrypt function)
    no password required.
    
  """
  
  with open(input_file, 'rt') as f_in: 
    r_b64_data = f_in.read()
  b64_data = reverse_str(r_b64_data)
  b64_decoded_data = base64_decode(input_data=b64_data, output="byte") 
  unzip_data =  do_unzip(input_data=b64_decoded_data, output_file=output_file, output="file")
  pass

####################################################################################################


def replace_text_files(replace_keys, files, casesesitive=True):
  """
    usage  : replace text in list of files/single file
    params : 
      oldkeys = old keys to be replaced
      newkeys = new keys to replace old one
      type    = text  
      casesesitive = True (default) | False
    returns : 
      dictionary {} includes files which has been changed     

    sample input :
      result = replace_text_files([('a','a_new'), ('b', 'b_xxx')], ['R:/1.txt','R:/2.txt','R:/3.txt'] )
    
    sample output :
      {
       file1: True,  # file1 changed
       file2: False, # file2 NOT changed
       file3: True   # file3 changed
      }

  """

  result = {}
  if isinstance(files, str) :
    files = [files]

  if isinstance(replace_keys, tuple) :
    replace_keys = [replace_keys]

  for f in files :
    f_text = read_file(f,return_type='str')
    result[f] = False
    for oldkey, newkey in replace_keys:
      if casesesitive == True:
        f_text, count = re.subn(oldkey, newkey, f_text)
      else:
        f_text, count = re.subn(oldkey, newkey, f_text,flags = re.IGNORECASE)
      
      if count > 0 : 
        result[f] = True
        write_file(file_name=f, text = f_text, mode="w")

  return result





if __name__ == "__main__":
  #print (len( get_files (folder="R:/", type='file')))
  """
  for f in gen_files (folder="Y:/important", type='file'):
    print (f)
  

  #print (base64_encode(input_file="R:/panda.jpg",output_file="R:/panda.jpg.b64", output="text"))
  #print (base64_decode(input_file="R:/panda.jpg.b64",output_file="R:/panda1.jpg", output="text"))
  encrypt(input_file="R:/panda.jpg",output_file="R:/panda.jpg.encrypted")
  
  

  decrypt(input_file="R:/panda.jpg.encrypted",output_file="R:/panda_restored.jpg")
  #rm_folder ("R:/", empty=True)
  #print (replace_text_files.__doc__)
  #result = replace_text_files([('http_proxy.*',''), ('b.*', 'BB')], ['R:/1.txt','R:/2.txt','R:/3.txt'],casesesitive=False )

  #print (result)
  
  print(delete_folder.__doc__)
  delete_folder("R:/temp1", empty=False)
  mk_folder("r:/temp1/t1/t2") 
  print (get_file_folder("r:/temp1/t1/t2/t3/file1.txt") )
  print(get_file_name("r:/temp1/t1/t2/t3/file1.txt") )
  print(parse_full_path("r:/temp1/t1/t2/t3/file1.txt") )
  clean_folder("r:/temp1/t1/t2") 
  """
  
  
  """
  split_file(input_file='R:/Temp2/disk.bin',output_folder='R:/Temp2', volume_size=1234)
  join_file(input_file='R:/Temp2/disk.bin', output_folder ='R:/Temp1')
  
  print (get_md5('R:/Temp2/disk.bin'))
  print (get_md5('R:/Temp1/disk.bin'))
  
  """
  """
  clean_folder('R:/TempVM/stage')
  #rm_folder(folder_name='R:/TempVM/stage')
  """
  """
  rm_file(file_name = 'r:/temp1/1.txt') 
  rm_file(file_name = ['r:/temp1/1.txt', 'r:/temp1/3.txt'] ) 
  rm_file(folder = 'R:/temp1', regex_pattern='\d+\.txt' ) 
  """
  
  """
  print (compare_files ( 'R:/TempVM/download/866c6e0a2795e52fc8c99211736a4f70.part_00001', 'R:/TempVM/upload/866c6e0a2795e52fc8c99211736a4f70.part_00000'))
  """
  for f in gen_files(folder="R:/Temp2", recursive=True, ext="", type='all'):
    print (f)
  
  for f in get_files(folder="R:/Temp2", recursive=True, ext="", type='F'):
    print (f)

  
  pass
  