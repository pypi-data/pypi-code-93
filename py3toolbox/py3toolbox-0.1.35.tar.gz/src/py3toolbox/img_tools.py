import os
import numpy as np
import exifread


def get_exif(path):
  with open(path, 'rb') as f:
    tags = exifread.process_file(f)

  return tags


def img2array(img_file) :
  img=np.asarray(Image.open(img_file))
  print (img)
  print(img.shape)
  
  
if __name__== "__main__" :
  print(get_exif("R:/abc.jpg"))
