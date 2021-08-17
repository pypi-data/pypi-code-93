import boto3
from urllib.parse import urlparse
from botocore.exceptions import ClientError
import ntpath


class S3Helper:

    def __init__(self, *args, **kwargs):
        '''

        :param args:
        :param kwargs:
        key like
        '''
        self.s3_hook = kwargs.get('s3_hook')

    def upload(self, source_file=None, s3_path=None, bucket=None, prefix=None, s3_hook=None, profile=None, replace=False, **kwargs):

        if not bucket:
            bucket, prefix = self.parse_s3_url(s3_path)

        key = prefix + ntpath.basename(source_file)

        if str(key).strip()[-1] == '/':
            raise ValueError("The key {key} is a folder ".format(key=key))

        if not profile:
            profile = bucket

        if s3_hook:
            conn = s3_hook.get_conn()
        elif self.s3_hook:
            conn = self.s3_hook.get_conn()
        else:
            session = boto3.Session(profile_name=profile)
            conn = session.client('s3')

        if not replace and self.check_for_key(conn, bucket, key):
            raise ValueError("The key {key} already exists.".format(key=key))

        conn.upload_file(source_file, bucket, key)
        print('upload success')

    def check_for_key(self, conn, bucket, key):
        """
        Checks if a key exists in a bucket

        :param key: S3 key that will point to the file
        :type key: str
        :param bucket_name: Name of the bucket in which the file is stored
        :type bucket_name: str
        """

        try:
            conn.head_object(Bucket=bucket, Key=key)
            return True
        except ClientError as e:
            print(e.response["Error"]["Message"])
            return False

    def download(self, s3_path=None, target_file=None, bucket=None, key=None, s3_hook=None, profile=None, **kwargs):
        '''

        :param s3_path:  s3://srs-vendors/72degree/luckin/ we can get bucket, prefix, profile from this path
        :param target_file: the local file
        :param bucket: if we have a s3 path, we don't need a bucket, prefix
        :param key:
        :param s3_hook: airflow s3 hook, it contains the conn info
        :return:
        '''

        if not bucket:
            bucket, key = self.parse_s3_url(s3_path)

        if str(key).strip()[-1] == '/':
            raise ValueError("The key {key} is a folder ".format(key=key))

        if not profile:
            profile = bucket

        if s3_hook:
            conn = s3_hook.get_conn()
        elif self.s3_hook:
            conn = self.s3_hook.get_conn()
        else:
            session = boto3.Session(profile_name=profile)
            conn = session.client('s3')

        conn.download_file(bucket, key, target_file)

    @staticmethod
    def parse_s3_url(s3url):
        parsed_url = urlparse(s3url)
        if not parsed_url.netloc:
            raise Exception('Please provide a bucket_name instead of "%s"' % s3url)
        else:
            bucket = parsed_url.netloc
            key = parsed_url.path.lstrip('/')
            return bucket, key



if __name__ == '__main__':
    t = S3Helper()
    file = r'D:\git\github\72degree-will\degree72_simple\Util\test.csv'
    # t.upload(file=file, bucket='srs-vendors', key='72degree/trip_auction/test/sub_test/')
    # t.upload(file=file, s3_path='/72degree/trip_auction/test/sub_test/')
    t.upload(source_file=file, s3_path='s3://srs-vendors/72degree/trip_auction/test/sub_test/')
