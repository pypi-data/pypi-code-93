# coding: utf8
from gevent import spawn
from flask import abort, request
import ujson as json
import hmac
import hashlib

from farbox_bucket.utils import smart_str
from farbox_bucket.server.web_app import app
from farbox_bucket.bucket.token.utils import get_logined_bucket

from farbox_bucket.server.utils.response import force_redirect, p_redirect

from farbox_bucket.clouds.utils import get_cloud_site_folder_for_bucket
from farbox_bucket.clouds.dropbox.utils import Dropbox_APP_SECRET, set_dropbox_cursor, get_dropbox_cursor, clear_dropbox_cursor
from farbox_bucket.clouds.dropbox.dropbox_client import sync_by_dropbox_client
from farbox_bucket.clouds.dropbox.dropbox_auth_token import DropboxAuthClient, has_dropbox_account, \
    get_dropbox_account, delete_dropbox_account

from farbox_bucket.server.template_system.api_template_render import render_api_template_as_response





@app.route("/__dropbox/bind", methods=["POST", "GET"])
def dropbox_endpoint():
    bucket = get_logined_bucket(check=True)
    if not bucket:
        return force_redirect("/login")
    if request.values.get("action") == "jump":
        auth_client = DropboxAuthClient()
        auth_url = auth_client.get_auth_url()
        if not auth_url:
            abort(404, "get auth-url failed")
        else:
            return p_redirect(auth_url)
    else: # display
        dropbox_account = get_dropbox_account(bucket=bucket) or {}
        dropbox_account_id = dropbox_account.get("account_id")
        if request.values.get("action") == "reset_cursor" and dropbox_account_id:
            clear_dropbox_cursor(dropbox_account_id, bucket=bucket) # reset cursor
        elif request.values.get("action") == "unbind" and dropbox_account_id:
            delete_dropbox_account(dropbox_account_id, bucket=bucket)
            dropbox_account = {}
        dropbox_cursor = get_dropbox_cursor(account_id=dropbox_account_id, bucket=bucket) or ""

        cloud_site_folder = get_cloud_site_folder_for_bucket(bucket) or bucket
        response = render_api_template_as_response("dropbox_bind.jade",
                                                   cloud_site_folder = cloud_site_folder,
                                                   dropbox_account = dropbox_account,
                                                   dropbox_cursor = dropbox_cursor)
        return response



@app.route("/__dropbox/callback", methods=["POST", "GET"])
def dropbox_callback_endpoint():
    bucket = get_logined_bucket(check=True)
    if not bucket:
        return force_redirect("/login")
    auth_client = DropboxAuthClient()
    auth_client.calback()
    return p_redirect("/__dropbox/bind?status=done")



def validate_dropbox_request(message):
    '''Validate that the request is properly signed by Dropbox.
       (If not, this is a spoofed webhook.)'''
    signature = request.headers.get('X-Dropbox-Signature')
    signature_to_check = hmac.new(smart_str(Dropbox_APP_SECRET), smart_str(message), hashlib.sha256).hexdigest()
    return signature == signature_to_check


#### hook 相关, 获得 dropbox 的 hook 通知，并进行同步
@app.route("/__dropbox/webhook", methods=["POST", "GET"])
def dropbox_webhook():
    if request.method == 'GET': # 验证dropbox 自身 webhook的可用性
        return request.args.get('challenge')
    elif request.method == 'POST':
        # Make sure this is a valid request from Dropbox
        if not validate_dropbox_request(request.data):
            abort(403)
        data = json.loads(request.data)
        # for uid in data['delta']['users']:
        for account_id in data["list_folder"]["accounts"]:
            if not has_dropbox_account(account_id):
                continue
            else:
                spawn(sync_by_dropbox_client, account_id) # 异步处理，因为sync本身会耗费一些时间
        return ''
    else:
        abort(403)