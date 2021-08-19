# -*- coding:utf-8 -*-
import time

from commFunction import *
import shutil
from POLQA import startvqt,vqtDisConnect




def polqa_client_test(src,test):
    exec_shell_command('cd /home/netease/polqa_result \n rm -rf *')
    curip = getip()
    curtime = log_time()
    curpath = str(curip) + '_'+str(curtime)
    os.mkdir(curpath)
    filename = curpath+'/'+ curpath+ '.dat'
    print(os.path.basename(src),os.path.basename(test))
    with open(filename,'w+')as wf:
        wf.writelines(os.path.basename(src)+'\n')
        wf.writelines(os.path.basename(test) + '\n')
    #ssh
    shutil.copy(src,curpath)
    shutil.copy(test, curpath)

    dstpath = '/home/netease/polqa'


    # stfp
    client,sftp = sftp_connect(username,password,serverIP,port=port)
    sftp_put(sftp,curpath, dstpath)
    sftp_disconnect(client)

    shutil.rmtree(curpath)
    # get result
    remote = '/home/netease/polqa_result/' + curpath + '.res'
    local = 'result' +'/' + curpath + '.res'
    while(1):
        # 下载文件
        resout = exec_shell_command('[ -f "{}" ] && echo true || echo false'.format(remote))
        resultflag = bytes.decode(resout).split()[0]
        if resultflag== 'true':
            client, sftp = sftp_connect(username, password, serverIP, port=port)
            sftp_get(sftp, remote, 'result')
            sftp_disconnect(client)
            #删除服务器文件
            exec_shell_command('rm -rf ' + remote)

            with open(local,'r') as rf:
                info = rf.readlines()
            print(info)
            os.remove(local)
            break
        else:
            continue

if __name__ == '__main__':
    # client, sftp = sftp_connect(username, password, serverIP, port=port)
    # sftp_get(sftp, '/home/netease/polqa_result/' + '192.168.1.3_2021-08-18-17-52-35' + '.ress', 'result')
    path = r'E:\02_POLQA_RESULT\testDstFiles\NERTC_iphone11_honor8x_V4.3.0\L\Speech_48000\NONE\female\femalePOLQASWB'
    src = r'E:\01_MOS_AUTO_TESTER\testSrcFiles\Speech_48000\female\femalePOLQASWB.pcm'
    filelist = []
    get_file_path(path,filelist,[])
    print(filelist)
    #print(exists_remote('10.219.33.45','/home/netease/polqa_result/455.ss'))
    for file in filelist:
        startvqt(src, file,48000)
    vqtDisConnect
    # for a in range(100):
    #     polqa_client_test(srcfile,testfile)
