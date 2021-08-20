import sys;from sys import stdin,stdout
终端输入=stdin
终端输出=stdout
错误输出=sys.stderr
class 终端(object):
    def __init__(self):
        self.终端输入=终端输入
        self.终端输出=终端输出
        self.错误输出中心=错误输出
    def 打印(self,*args):
        print(*args)
    def 输入一行(self,提示):
        return input(提示)
    def 错误输出(self,*args):
        for i in args:
            self.错误输出中心.write(i)
            self.错误输出中心.write('\n')
            self.错误输出中心.flush()
    def 刷新(self,要刷新的内容=[stdin,stdout,错误输出]):
        for i in 要刷新的内容:
            i.flush()
