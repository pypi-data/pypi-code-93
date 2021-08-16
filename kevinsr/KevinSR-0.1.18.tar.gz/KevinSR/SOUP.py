import os
import numpy as np
from scipy import ndimage, interpolate
from scipy.ndimage import zoom
#import time
#import random
#import math
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.layers import Conv3D, MaxPooling3D, Conv3DTranspose, concatenate
import tensorflow.keras.backend as K
import urllib.request
import tarfile
#from processing import *


def SOUP_GAN(thicks_ori, Z_FAC,prep_type=0):

    thicks_ori = rescale_img(thicks_ori, max_val= 10000)

    thins = zoom(thicks_ori, (1,1,Z_FAC))
    
    filedir = os.path.dirname(os.path.abspath('__file__'))    

    isdir = os.path.isdir(filedir + '/Thick-to-thin')
    if isdir == False:
        url = 'https://drive.google.com/uc?export=download&id=1PM9I7ccZP4zTocQqIFN5EEdJKdahvp4j'
        urllib.request.urlretrieve(url,filedir+'/Thick-to-thin.tar.bz2')
        tar = tarfile.open(filedir+'/Thick-to-thin.tar.bz2',"r:bz2")
        tar.extractall()
        tar.close()

    isdir = os.path.isdir(filedir + '/Thin-to-thin')
    if isdir == False:
        url = 'https://drive.google.com/uc?export=download&id=10cJLBy7EMXqXHhVvqCXLc5fKZpooy9w5'
        urllib.request.urlretrieve(url,filedir+'/Thin-to-thin.tar.bz2')
        tar = tarfile.open(filedir+'/Thin-to-thin.tar.bz2',"r:bz2")
        tar.extractall()
        tar.close()



    if prep_type == 0:
        new_model=keras.models.load_model(filedir + '/Thick-to-thin')
    elif prep_type == 1:
        new_model=keras.models.load_model(filedir + '/Thin-to-thin')
    thins_gen = thins.copy()

    target = np.moveaxis(thins,-1,0)
    target = target [...,np.newaxis]
    target = target [np.newaxis,...]

    index  = attention_coeff(target, Z_FAC)

    target = new_model.predict([target,index])
     
    target_small = target[0,...,0]
    thins_gen = np.moveaxis(target_small, 0,-1)

    return thins_gen
     
def attention_coeff(target, Z):
    index  = np.zeros((target.shape[0],5))
    if Z < 2:
        index[:,0] =1
    elif Z < 3:
        t = Z-2
        index[:,0] = 1-t
        index[:,1] = t
    elif Z < 4:
        t = Z-3
        index[:,1] = 1-t
        index[:,2] = t
    elif Z < 5:
        t = Z-4
        index[:,2] = 1-t
        index[:,3] = t
    elif Z < 6:
        t = Z-5
        index[:,3] = 1-t
        index[:,4] = t
    else:
        index[:,4] = 1
    return index

MAX_VAL = 10000

def rescale_img(image, max_val=MAX_VAL):
    image = image - np.min(image)
    image = (np.maximum(image, 0) / image.max()) * max_val
    return (image)

