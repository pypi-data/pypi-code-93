# coding: utf8
from flask import abort, request
from farbox_bucket.settings import sentry_client
from farbox_bucket.utils import string_types
from farbox_bucket.bucket.token.utils import get_logined_bucket
from farbox_bucket.clouds.utils import get_cloud_callback_url
from farbox_bucket.server.utils.cookie import get_cookie, save_cookie
from farbox_bucket.server.utils.response import force_redirect
from farbox_bucket.utils.ssdb_utils import hset, hget, hexists, hdel

from dropbox import DropboxOAuth2Flow
from dropbox.oauth import OAuth2FlowResult
from dropbox.oauth import NotApprovedException, CsrfException, BadStateException, BadRequestException, ProviderException

from farbox_bucket.clouds.dropbox.utils import Dropbox_APP_KEY, Dropbox_APP_SECRET



def has_dropbox_account(dropbox_account_id):
    if not isinstance(dropbox_account_id, string_types):
        return False
    return hexists("dropbox_account", dropbox_account_id)

def get_dropbox_account(dropbox_account_id=None, bucket=None):
    if not dropbox_account_id and bucket:
        dropbox_account_id = hget("dropbox_bucket", bucket)
    if not dropbox_account_id and not bucket:
        return
    dropbox_account = hget("dropbox_account", dropbox_account_id, force_dict=True)

    if bucket and dropbox_account:
        buckets_in_account = dropbox_account.get("buckets") or []
        if not isinstance(buckets_in_account, list):
            buckets_in_account = []
        if bucket not in buckets_in_account:
            # 不应该出现的情况
            return

    return dropbox_account

def get_buckets_from_dropbox_account_id(dropbox_account_id, bucket=None):
    old_dropbox_account = get_dropbox_account(dropbox_account_id=dropbox_account_id)
    buckets = old_dropbox_account.get("buckets") or []
    if not isinstance(buckets, list):
        buckets = []
    if bucket and bucket not in buckets:
        # 新增的 buckets， 比如新绑定的
        buckets.append(bucket)
    return buckets

def create_dropbox_account(dropbox_account_id, bucket, account_data):
    if not isinstance(account_data, dict):
        return
    if not dropbox_account_id:
        return
    buckets = get_buckets_from_dropbox_account_id(dropbox_account_id, bucket=bucket)
    account_data["buckets"] = buckets
    hset("dropbox_account", dropbox_account_id, account_data, ignore_if_exists=False)
    hset("dropbox_bucket", bucket, dropbox_account_id)


def delete_dropbox_account(dropbox_account_id, bucket):
    if isinstance(dropbox_account_id, dict):
        dropbox_account_id = dropbox_account_id.get("account_id")
    if not isinstance(dropbox_account_id, string_types):
        return
    if not dropbox_account_id:
        return
    buckets = get_buckets_from_dropbox_account_id(dropbox_account_id)
    try: buckets.remove(bucket)
    except: pass
    if not buckets:
        # 没有 bucket 了，直接进行 account 的删除
        hdel("dropbox_account", dropbox_account_id)
    else:
        # 更新 buckets 的字段
        update_dropbox_account(dropbox_account_id, buckets=buckets)



def update_dropbox_account(dropbox_account_id=None, bucket=None, **kwargs):
    dropbox_account = get_dropbox_account(dropbox_account_id=dropbox_account_id, bucket=bucket)
    if not dropbox_account:
        return
    if not dropbox_account_id:
        dropbox_account_id = dropbox_account.get("account_id")
    if not dropbox_account_id:
        return
    dropbox_account.update(kwargs)
    hset("dropbox_account", dropbox_account_id, dropbox_account, ignore_if_exists=False)



csrf_key_name = "dropbox-auth-csrf-token"
class DropboxSession(dict):
    def __init__(self, csrf_name):
        dict.__init__(self, {csrf_name: get_cookie(csrf_name)})

    def __setitem__(self, key, value):
        # 设置 cookie
        save_cookie(key, value)



class DropboxAuthClient(object):
    def __init__(self):
        callback_url = get_cloud_callback_url("dropbox")
        self.flow = DropboxOAuth2Flow(consumer_key=Dropbox_APP_KEY, consumer_secret=Dropbox_APP_SECRET,
                                      redirect_uri=callback_url,
                                      session=DropboxSession(csrf_key_name),
                                      csrf_token_session_key=csrf_key_name,
                                      token_access_type = "offline")




    def get_auth_url(self):
        bucket = get_logined_bucket()
        if not bucket:
            return None
        try:
            url = self.flow.start()
        except:
            if sentry_client:
                sentry_client.captureException()
            url = None
        return url


    def calback(self):
        bucket = get_logined_bucket()
        if not bucket:
            return force_redirect("/login")
        query_params = request.args.to_dict()
        try:
            flow_result = self.flow.finish(query_params) # FlowResult
            if not isinstance(flow_result, OAuth2FlowResult):
                abort(404, "not valid OAuth2FlowResult from Dropbox")
            #flow_result.refresh_token
            account_data = dict(
                # user_id = flow_result.user_id,
                account_id = flow_result.account_id,
                expires_at = flow_result.expires_at, # datetime
                refresh_token = flow_result.refresh_token,
                access_token = flow_result.access_token
            )
            create_dropbox_account(flow_result.account_id, bucket, account_data)

            # 创建一个 bucket 对应的目录
            from farbox_bucket.clouds.dropbox.dropbox_client import DropboxClient
            dropbox_client = DropboxClient(account_id=flow_result.account_id, bucket=bucket)
            dropbox_client.create_site_folder()

        except BadRequestException:
            abort(400)
        except BadStateException:
            return force_redirect('/__dropbox/bind?source=bad_state')
        except CsrfException:
            abort(403)
        except NotApprovedException:
            return 'not approved'
        except ProviderException:
            if sentry_client: sentry_client.captureException()
            abort(403)
        except:
            if sentry_client: sentry_client.captureException()
            abort(400)