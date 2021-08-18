# coding: utf8
import time
from flask import request
from farbox_bucket.utils import string_types
from farbox_bucket.utils.objectid import ObjectId
from farbox_bucket.utils.ssdb_utils import hset, hget, hscan
from farbox_bucket.bucket.record.get.utils import to_py_records_from_raw_ssdb_records
from farbox_bucket.bucket.service.bucket_service_info import change_bucket_expired_date

def get_invitations(limit=100, start_code=None):
    # return the list, 跟 Record 的逻辑一样转换数据
    raw_records = hscan("_bucket_invite", key_start=start_code, limit=limit, reverse_scan=True)
    records = to_py_records_from_raw_ssdb_records(raw_records)
    return records


def create_invitations(limit=3, note="", years=0):
    # 邀请码是连续的，不要一次性创建太多
    for i in range(limit):
        if note:
            i_note = "%s %s" % (i+1, note)
        else:
            i_note = ""
        create_invitation(i_note, years=years)


def get_invitation(code):
    # 邀请码是 code 也是 id
    record = hget('_bucket_invite', code) or {}
    return record


def create_invitation(note="", years=0):
    code = str(ObjectId())
    info_doc = dict(
        _id = code,
        created_at = time.time(),
        note = note,
        years = years,
    )
    hset('_bucket_invite', key=code, value=info_doc)


def use_invitation(code, bucket):
    code = code.strip()
    invitation = get_invitation(code)
    if not invitation or not isinstance(invitation, dict):
        return False
    else:
        invitation["bucket"] = bucket
        invitation["used_at"] = time.time()
        hset('_bucket_invite', key=code, value=invitation)

        # 邀请自带了 bucket 有效期的延期
        years = invitation.get("years")
        if years and isinstance(years, (int, float)):
            days = 366 * years
            change_bucket_expired_date(bucket=bucket, days=days)

        return True


def can_use_invitation(code):
    if not code or not isinstance(code, string_types):
        return False
    code = code.strip()
    invitation = get_invitation(code)
    if not invitation:
        return False
    if invitation.get("bucket"): # 已经被使用了
        return False
    else:
        return True



def check_invitation_by_web_request():
    invitation_code = request.values.get('code') or request.values.get("invitation") or request.values.get("invitation_code")
    return can_use_invitation(invitation_code)







