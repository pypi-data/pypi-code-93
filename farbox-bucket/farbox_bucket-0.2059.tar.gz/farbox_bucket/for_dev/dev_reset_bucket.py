#coding: utf8
import os, time


def reset_bucket_for_dev(bucket, ssdb_ip=None):
    # 会把整个 Bucket 全部删除掉
    if ssdb_ip:
        os.environ['SSDB_IP'] = ssdb_ip #'192.168.99.100'
    from farbox_bucket.bucket.utils import clear_related_buckets
    from farbox_bucket.bucket.record.reset import reset_related_records
    clear_related_buckets(bucket)
    reset_related_records(bucket)


if __name__ == "__main__":
    reset_bucket_for_dev('671825f0c28b8f1873f48eb757aa45560334c825', ssdb_ip='192.168.99.100')
