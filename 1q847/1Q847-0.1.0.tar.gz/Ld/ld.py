import os
from subprocess import Popen, PIPE

class 雷电命令:
    def __init__(self):
        self.path = os.path.split(os.path.realpath(__file__))[0]
        os.putenv('Path', self.save_dir())

        print(self.path)
    def save_dir(self):
        with open(self.path+'\dir.txt','a+') as p:
            p.read()
        with open(self.path+'\dir.txt', 'r+') as  p:
            a = p.read()
            if len(a) == 0:
                b = self.get_dir()

                p.write(b)
                a = b
            return a

    def get_dir(self):
        path_list = ['C:\\', 'D:\\', 'E:\\', 'F:\\']
        for path in path_list:
            for root, dirs, files, in os.walk(path):

                for f in files:
                    if f == 'ldconsole.exe':
                        print('模拟器路径获取成功')
                        return root
        assert False,'模拟器路径不存在'

    def 读取命令信息(self, cmd):
        res = Popen(cmd, stdout=PIPE, shell=True)
        res = res.stdout.read().decode(encoding='GBK')
        return res

    def 启动模拟器(self, order):
        self.读取命令信息('ldconsole.exe launch --index ' + order)

    def 关闭模拟器(self, order):
        self.读取命令信息(cmd='ldconsole.exe quit --index ' + order)

    def 获取模拟器信息(self):
        return self.读取命令信息('ldconsole.exe  list2')
        # 索引，标题，顶层窗口句柄，绑定窗口句柄，是否进入android，进程PID，VBox进程PID

    def 新增模拟器(self, name):
        self.读取命令信息('ldconsole.exe add --name ' + name)

    def 删除模拟器(self, order):
        self.读取命令信息('ldconsole.exe remove --index ' + order)

    def 复制模拟器(self, name, order):
        self.读取命令信息('ldconsole.exe copy --name ' + name + ' --from ' + order)

    def 启动APP(self, order, packagename):
        self.读取命令信息('ldconsole.exe runapp --index ' + order + ' --packagename ' + packagename)

    def 关闭APP(self, order, packagename):
        self.读取命令信息('ldconsole.exe killapp --index ' + order + ' --packagename ' + packagename)

    def 获取包名(self, order):
        return self.读取命令信息(cmd='ld.exe -s ' + str(order) + '  pm list packages')

    def 安装APP(self, order, path):
        self.读取命令信息('ldconsole.exe  installapp --index ' + order + ' --filename ' + path)


if __name__ == '__main__':
    ld = 雷电命令()
    ld.启动模拟器('0')
