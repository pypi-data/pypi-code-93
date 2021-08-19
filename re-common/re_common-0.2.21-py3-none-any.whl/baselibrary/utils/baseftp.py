from ftplib import FTP


class BaseFtp(object):
    def __init__(self,encoding='utf-8'):
        self.ftp = FTP()
        self.ftp.encoding = encoding

    def conn_ftp(self,FtpHost):
        self.ftp.connect(FtpHost, 21)
        return self

    def login(self,username,passwd):
        self.ftp.login(username,passwd)

    def cwd(self,dires):
        """
        执行ftp命令
        :param dires:
        :return:
        """
        self.ftp.cwd(dires)  # change remote work dir

    def getfilesize(self,remotefile):
        return self.ftp.size(remotefile)

    def voidcmd(self):
        """
        :return:
        """
        self.ftp.voidcmd('TYPE I')