#coding: utf8
from farbox_bucket.utils.ssdb_utils import zscan


def loop_buckets_and_run(func_to_run, limit=1000):
    score_start = ""
    last_bucket = ""
    buckets_done = []
    while True:
        result = zscan("buckets", score_start=score_start, limit=limit)
        cursor = ""
        bucket = ""
        for (bucket, cursor) in result:
            if bucket == last_bucket: # 已经处理过了， 相同的 cursor 可能有多个 bucket，所以本身是包含的
                continue
            done = func_to_run(bucket)
            if done:
                buckets_done.append(bucket)
        if not cursor: # result is empty
            break
        # next loop
        score_start = cursor
        last_bucket = bucket
        if len(result) != limit: # no need to next lopp
            break
    return buckets_done
