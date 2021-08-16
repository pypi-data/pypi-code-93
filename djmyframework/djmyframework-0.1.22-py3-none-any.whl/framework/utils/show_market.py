# -*- coding: utf-8 -*-
# @Author: xzregg
# 

import os
import sys
import struct
import shutil
import argparse
import time
import traceback

__version__ = '1.0.7'  # 2016.08.09

ZIP_SHORT = 2

MAGIC = '!ZXK!'



def add_channel_to_apk(apkfile,c1,c2,output='',new_file_name=''):
    try:
        the_abs_dir = output or os.path.dirname(os.path.abspath(apkfile))
    
        src_apk_file_name = os.path.basename(apkfile)
        channel_identifying = '%s^%s' % (c1,c2)
        
        apk_file = write_market(apkfile,channel_identifying,the_abs_dir,new_file_name)
        
        return apk_file,read_market(apk_file) == channel_identifying,''
    except Exception as e:
        traceback.print_exc()
        return '',False,str(e)


def write_market(path, market, output,new_file_name=''):
    '''
    write market info to apk file
    write_market(apk-file-path, market-name, output-path)
    '''
    path = os.path.abspath(path)
    output = str(output)
    if not os.path.exists(path):
        print(('apk file', path, 'not exists'))
        return
    if read_market(path):
        print(('apk file', path, 'had market already'))
        return
    if not output:
        output = os.path.dirname(path)
    if not os.path.exists(output):
        os.makedirs(output)
    name, ext = os.path.splitext(os.path.basename(path))
    name_sp = name.split('_')
    if name[0].isdigit():
        name_sp = name_sp[1:]
    if len(name_sp) >= 2:
        name = '%s_%s' % (name_sp[0],name_sp[1])
    else:
        name = name_sp[0]
    apk_name = new_file_name or '%s_%s%s'  % (name, market.replace('^','_') , ext)
    apk_file = os.path.join(output, apk_name)
    shutil.copy(path, apk_file)

    index = os.stat(apk_file).st_size
    index -= ZIP_SHORT
    with open(apk_file, "r+b") as f:
        f.seek(index)
        # write comment length
        f.write(struct.pack('<H', len(market) + ZIP_SHORT + len(MAGIC)))
        # write comment content
        # content = [market_string + market_length + magic_string]
        f.write(market)
        f.write(struct.pack('<H', len(market)))
        f.write(MAGIC)
    return apk_file


def read_market(path):
    '''
    read market info from apk file
    read_market(apk-file-path)
    '''
    index = os.stat(path).st_size
    # print('path:',path,'length:',index)
    index -= len(MAGIC)
    f = open(path, 'rb')
    f.seek(index)
    # read and check magic
    magic = f.read(len(MAGIC))
    # print('magic',magic)
    if magic == MAGIC:
        index -= ZIP_SHORT
        f.seek(index)
        # read market string length
        market_length = struct.unpack('<H', f.read(ZIP_SHORT))[0]
        # print('comment length:',market_length)
        index -= market_length
        f.seek(index)
        # read market
        market = f.read(market_length)
        # print('found market:',market)
        return market
    else:
        # print('magic not matched')
        return None


def verify_market(path, market):
    '''
    verify apk market info
    verify_market(apk-file-path,market-name)
    '''
    return read_market(path) == market


def show_market_from_dir(dir_pant):
    for dirpath, dirs, files in os.walk(dir_pant):
                for filename in files:
                    if  filename.endswith('.apk'):
                        file_name = os.path.join(dirpath,filename)
                        print((file_name,read_market( file_name)))

if __name__ == '__main__':
    print((sys.argv))
    if len(sys.argv) > 1:
        print((show_market_from_dir(sys.argv[1])))
