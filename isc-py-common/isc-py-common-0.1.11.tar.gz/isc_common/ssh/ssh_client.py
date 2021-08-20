import logging
import os
import socket
import traceback

import paramiko
from django.conf import settings

logger = logging.getLogger(__name__)


class SSH_Client:
    def __init__(self, hostname, username, password, port=22):

        hostkey = None
        try:
            host_keys = paramiko.util.load_host_keys(
                os.path.expanduser("~/.ssh/known_hosts")
            )
        except IOError:
            try:
                # try ~/ssh/ too, because windows can't have a folder named ~/.ssh/
                host_keys = paramiko.util.load_host_keys(
                    os.path.expanduser("~/ssh/known_hosts")
                )
            except IOError:
                logger.debug("*** Unable to open host keys file")
                host_keys = {}

        if hostname in host_keys:
            hostkeytype = host_keys[hostname].keys()[0]
            hostkey = host_keys[hostname][hostkeytype]
            logger.debug("Using host key of type %s" % hostkeytype)

        try:
            t = paramiko.Transport((hostname, port))
            t.connect(
                hostkey,
                username,
                password,
                gss_host=socket.getfqdn(hostname),
                gss_auth=False,
                gss_kex=False,
            )
            self.sftp = paramiko.SFTPClient.from_transport(t)
        except Exception as e:
            logger.error("*** Caught exception: %s: %s" % (e.__class__, e))
            traceback.print_exc()
            try:
                self.t.close()
            except:
                pass

    def get(self, remotepath, localpath, callback=None):
        try:
            self.sftp.get(remotepath=remotepath, localpath=localpath, callback=callback)
        except IOError as ex:
            logger.error(f'{remotepath} {str(ex)}')

    def put(self, localpath, remotepath, callback=None, confirm=True):
        try:
            self.sftp.put(localpath=localpath, remotepath=remotepath, callback=callback, confirm=confirm)
            return None
        except Exception as ex:
            logger.error(ex)
            return ex

    def exists(self, path):
        try:
            self.sftp.stat(path)
            return True
        except FileNotFoundError:
            return False

    def getsize(self, path):
        return self.sftp.stat(path).st_size

    def open(self, filename, mode="r", bufsize=-1):
        return self.sftp.open(filename=filename, mode=mode, bufsize=bufsize)

    def remove(self, path):
        try:
            self.sftp.remove(path=path)
        except Exception as ex:
            logger.error(ex)

    def chmod(self, path, mode):
        try:
            self.sftp.chmod(path=path, mode=mode)
        except Exception as ex:
            logger.error(ex)

    def rename(self, oldpath, newpath):
        try:
            self.sftp.rename(oldpath=oldpath, newpath=newpath)
        except Exception as ex:
            logger.error(ex)


class SSH_Client_settings(SSH_Client):
    def __init__(self):
        SSH_Client.__init__(
            self,
            hostname=settings.FILES_STORE.get('SSH_HOST'),
            username=settings.FILES_STORE.get('SSH_USER'),
            password=settings.FILES_STORE.get('SSH_PASSWORD'),
            port=settings.FILES_STORE.get('SSH_PORT')
        )
