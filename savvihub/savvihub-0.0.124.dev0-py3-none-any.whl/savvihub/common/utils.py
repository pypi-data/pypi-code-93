import concurrent.futures
import json
import os
import random
import shutil
import string
import uuid
import zlib
from datetime import datetime, timedelta, timezone

import timeago


def make_file(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    if not os.path.exists(path):
        with open(path, 'w'):
            print(" [*] Make a file : {}".format(path))
            pass


def make_dir(path):
    if not os.path.exists(path):
        print(" [*] Make directories : {}".format(path))
        os.makedirs(path)


def remove_file(path):
    if os.path.exists(path):
        print(" [*] Removed: {}".format(path))
        os.remove(path)


def remove_dir(path):
    if os.path.exists(path):
        print(" [*] Removed: {}".format(path))
        shutil.rmtree(path)


def write_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, sort_keys=True, ensure_ascii=False)


def load_json(path):
    with open(path) as f:
        data = json.loads(f.read())
    return data


def calculate_crc32c(filename):
    try:
        with open(filename, 'rb') as fh:
            h = 0
            while True:
                s = fh.read(65536)
                if not s:
                    break
                h = zlib.crc32(s, h)
            return "%X" % (h & 0xFFFFFFFF)
    except Exception as e:
        import sentry_sdk
        sentry_sdk.capture_exception(e)
        sentry_sdk.flush()

        return ""


def read_in_chunks(filename, blocksize=65535, chunks=-1, callback=None):
    """Lazy function (generator) to read a file piece by piece."""
    with open(filename, 'rb') as f:
        while chunks:
            data = f.read(blocksize)
            if not data:
                break
            yield data

            if callback:
                callback(data)
            chunks -= 1


def wait_all_futures(futures):
    concurrent.futures.wait(futures)
    return [future.result() for future in futures]


def short_string(data, length):
    return (data[:length] + '..') if len(data) > length else data


def parse_str_time_to_datetime(time_str):
    return datetime.strptime(time_str, "%Y-%m-%dT%H:%M:%S.%fZ")


def parse_time_to_ago(dt: datetime):
    if not dt:
        return 'N/A'
    return timeago.format(dt, datetime.now(timezone.utc))


def parse_timestamp_or_none(timestamp):
    if not timestamp:
        return 'N/A'
    return datetime.fromtimestamp(timestamp)


def sizeof_fmt(num, suffix='B'):
    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Yi', suffix)


def remove_prefix(self: str, prefix: str) -> str:
    if self.startswith(prefix):
        return self[len(prefix):]
    else:
        return self[:]


def remove_suffix(self: str, suffix: str) -> str:
    # suffix='' should not call self[:-0].
    if suffix and self.endswith(suffix):
        return self[:-len(suffix)]
    else:
        return self[:]


def random_string(length=24, punctuations=False):
    letters = string.ascii_lowercase + string.digits
    if punctuations:
        letters += '!@#$^&'
    return random.SystemRandom().choice(string.ascii_lowercase) + ''.join(random.SystemRandom().choice(letters) for _ in range(length-1))


def random_uuid():
    return str(uuid.uuid4())


def random_date(start, end):
    delta = end - start
    random_days = random.randrange(delta.days)
    return start + timedelta(days=random_days)
