import boto
import boto.s3.connection
import boto.sqs
from boto.s3.connection import OrdinaryCallingFormat

from boto.sqs.message import RawMessage

class KeyBucketConnect(object):

    def __init__(self, folder, bucket_name=None, environment='development'):

        # O ideal seria o get_bucket ser um @classmethod, mas nao achei viavel
        # por ter a escolha do bucket baseado no parametro passado. Talvez separar em methodos
        # futuramento. Nao deu nenhum problema ate agora. unattis
        self.s3_conn = boto.connect_s3(calling_format=OrdinaryCallingFormat())
        self.bucket = self.s3_conn.get_bucket(bucket_name)
        self.folder = folder + environment

    def get_key(self, path):
        return self.bucket.get_key(path)

    def set(self, path, string, acl='public-read'):
        key = self.bucket.new_key(self.folder + path)
        key.set_contents_from_string(string)
        key.set_acl(acl)

    def set_from_file(self, path, file, acl='public-read'):
        key = self.bucket.new_key(self.folder + path)
        key.set_contents_from_file(file)
        key.set_acl(acl)

    def set_from_filename(self, path, file, acl='public-read'):
        key = self.bucket.new_key(self.folder + path)
        key.set_contents_from_filename(file)
        key.set_acl(acl)

    def list(self):
        return self.bucket.list(self.folder)

    def delete_key(self, key):
        return self.bucket.delete_key(key)


class SQSConnect(object):
    def __init__(self, region=None):
        self.server = boto.sqs.connect_to_region(region)
    def get_queue(self, queue):
        q = self.server.get_queue(queue)
        q.set_message_class(RawMessage)
        return q