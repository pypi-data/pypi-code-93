# -*- coding:utf-8 -*-
import time
import socket
import os
from commFunction import *
import shutil
import paramiko
from POLQA import cal_polqa


def exec_polqa_test():
    exec_shell_command('cd /home/netease/polqa \n rm -rf *')
    while(1):
        print('processing')
        #检查文件
        returnvalue = exec_shell_command('cd polqa \n ls')
        curdirlist = returnvalue.split()
        if len(curdirlist) != 0:
            print(curdirlist)
            #链接sftp
            client,sftp = sftp_connect(username,password,serverIP,port=port)
            curdir = bytes.decode(curdirlist[0])
            # 下载文件
            sftp_get(sftp,'/home/netease/polqa/'+curdir, '')
            sftp_disconnect(client)
            #删除服务器文件
            exec_shell_command('rm -rf /home/netease/polqa/' + curdir)
            with open(curdir +'/' + curdir + '.dat','r') as rf:
                info = rf.readlines()
            srcFile = curdir +'/'+ info[0].strip("\n")
            testFile = curdir +'/'+ info[1].strip("\n")
            #samplerate = info[3]
            print(os.path.abspath(srcFile),os.path.abspath(testFile))
            result = cal_polqa(os.path.abspath(srcFile),os.path.abspath(testFile),48000)
            print(result)
            shutil.rmtree(curdir)
            #结果上传服务器
            resfile = curdir + '.res'
            dstpath = '/home/netease/polqa_result'
            with open(resfile, 'w+')as wf:
                wf.writelines(str(result) + '\n')

            client, sftp = sftp_connect(username, password, serverIP, port=port)
            sftp_put(sftp, curdir + '.res', dstpath)
            sftp_disconnect(client)

            os.remove(resfile)
        else:
            time.sleep(1)

if __name__ == '__main__':
    # file = get_dir_list()
    # #print(get_dir_list())
    # print(del_spec_dir(bytes.decode(file[0]) ))
    exec_polqa_test()