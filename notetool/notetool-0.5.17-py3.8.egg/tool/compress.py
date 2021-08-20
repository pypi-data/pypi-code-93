import gzip
import os
import tarfile
import zipfile

"""
# gz： 即gzip。通常仅仅能压缩一个文件。与tar结合起来就能够实现先打包，再压缩。
# tar： linux系统下的打包工具。仅仅打包。不压缩
# tgz：即tar.gz。先用tar打包，然后再用gz压缩得到的文件
# zip： 不同于gzip。尽管使用相似的算法，能够打包压缩多个文件。只是分别压缩文件。压缩率低于tar。
# rar：打包压缩文件。最初用于DOS，基于window操作系统。
"""


def un_gz(file_path, target_path=None):
    """
    ungz zip file
    # gz
    # 因为gz一般仅仅压缩一个文件，全部常与其它打包工具一起工作。比方能够先用tar打包为XXX.tar,然后在压缩为XXX.tar.gz
    # 解压gz，事实上就是读出当中的单一文件
    """
    target_path = target_path or file_path.replace(".gz", "")
    target_path = target_path.replace(".tgz", ".tar")

    # 创建gzip对象
    with gzip.GzipFile(file_path) as g_file:
        # gzip对象用read()打开后，写入open()建立的文件里。
        open(target_path, "w+").write(g_file.read())
    return target_path


def un_tar(file_path, target_dir=None):
    """
    untar zip file
    # tar
    # XXX.tar.gz解压后得到XXX.tar，还要进一步解压出来。
    # 注：tgz与tar.gz是同样的格式，老版本号DOS扩展名最多三个字符，故用tgz表示。
    # 因为这里有多个文件，我们先读取全部文件名称。然后解压。例如以下：
    # 注：tgz文件与tar文件同样的解压方法。
    """
    target_dir = target_dir or file_path + "_files"

    with tarfile.open(file_path) as tar:
        names = tar.getnames()
        if not os.path.isdir(target_dir):
            os.mkdir(target_dir)

        # 因为解压后是很多文件，预先建立同名目录
        for name in names:
            tar.extract(name, target_dir)


def un_zip(file_path, target_dir=None):
    """
    unzip zip file
    """
    target_dir = target_dir or file_path + "_files"

    with zipfile.ZipFile(file_path) as zip_file:
        if not os.path.isdir(target_dir):
            os.mkdir(target_dir)
        for names in zip_file.namelist():
            zip_file.extract(names, target_dir)


def un_rar(file_path, target_dir=None):
    """
    unrar zip file
    # rar
    # 由于rar通常为window下使用，须要额外的Python包rarfile。
    #
    # 可用地址： http://sourceforge.net/projects/rarfile.berlios/files/rarfile-2.4.tar.gz/download
    #
    # 解压到Python安装文件夹的/Scripts/文件夹下，在当前窗体打开命令行,
    #
    # 输入Python setup.py install
    #
    # 安装完毕。
    """
    import rarfile
    target_dir = target_dir or file_path + "_files"
    with rarfile.RarFile(file_path) as rar:
        if not os.path.isdir(target_dir):
            os.mkdir(target_dir)
        os.chdir(target_dir)
        rar.extractall()


def decompress(file_path, target_dir=None):
    target_dir = target_dir or file_path + "_files"
    if not os.path.isdir(target_dir):
        os.mkdir(target_dir)

    file_name = os.path.basename(file_path)
    extension = file_name.split('.')[-1]
    if extension in ('gz', 'tgz'):
        target_path = un_gz(file_name)
        un_tar(target_path, target_dir)
    elif extension == 'zip':
        un_zip(file_path, target_dir)
    elif extension == 'rar':
        un_rar(file_path, target_dir)
    else:
        raise Exception('Not implement yet, please write the issue.')
