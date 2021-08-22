#coding: utf8
from farbox_bucket.utils import is_a_markdown_file, to_int, get_value_from_data
from farbox_bucket.utils.ssdb_utils import hscan, hclear, hset

from farbox_bucket.bucket.record.get.get import get_record
from farbox_bucket.bucket.utils import get_bucket_name_for_path, get_bucket_name_for_url, has_bucket
from farbox_bucket.bucket.record.utils import get_path_from_record, get_data_type, get_url_path





def repair_bucket_for_files(bucket, limit=20000):
    bucket_name_for_path = get_bucket_name_for_path(bucket)
    bucket_name_for_url = get_bucket_name_for_url(bucket)
    hclear(bucket_name_for_url) # 构建 URL 用得数据库进行清理

    if not has_bucket(bucket):
        return # ignore

    path_records = hscan(bucket_name_for_path, key_start='', limit=limit)
    storage_size = 0
    for filepath, filepath_data_string in path_records:
        lower_filepath = filepath.strip().lower()
        # prepare raw data starts
        raw_filepath_data = filepath_data_string.split(',')
        if len(raw_filepath_data) != 3:
            continue
        record_id, size, version =  raw_filepath_data
        size = to_int(size, default_if_fail=0)
        storage_size += size
        if version == "folder":
            continue

        # 构建 URL

        record =  get_record(bucket=bucket, record_id=record_id)
        if not record:
            continue

        # url 匹配用的索引
        path = get_path_from_record(record, strip_slash=True)
        if not path:
            continue

        url_path = get_url_path(record)
        # 两两对应的映射关系, 除了通过 url 找path，还可以 通过 path 找 url，因为删除一个 record 的时候，只有 path，没有 url_path
        if url_path:
            hset(bucket_name_for_url, url_path, path)
            if path != url_path:
                hset(bucket_name_for_url, path, url_path)


    # at last
    hset('_bucket_usage', bucket, storage_size)


