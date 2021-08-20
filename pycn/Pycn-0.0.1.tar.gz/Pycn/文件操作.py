def 打开(名称,编码="utf-8",方式="w+"):
    方式2=方式.replace("写+","w+").replace("读",'r').replace("写",'w').replace("文本",'t').replace("读+",'r+')
    file=open(名称,方式2,encoding=编码)
    return file
def 关闭(文件):
    文件.close()
def 写入(文件,文本=''):
    文件.write(文本)
def 读行(文件):
    w=文件.readline()
    return w
def 读所有行(文件):
    w=文件.readlines()
    return w
def 读取(文件):
    w=文件.read()
    return w
