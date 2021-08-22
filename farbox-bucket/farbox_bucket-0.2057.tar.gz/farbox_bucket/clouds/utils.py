#coding: utf8
from flask import request
from farbox_bucket.utils import string_types, get_value_from_data, smart_unicode
from farbox_bucket.bucket.utils import get_bucket_site_configs


def get_cloud_callback_url(service):
    try:
        #protocol = request.environ.get('HTTP_X_PROTOCOL') or 'http'
        protocol = 'https'
        host = request.host
    except:
        protocol = 'http'
        host = 'localhost'
    if 'localhost' in host: protocol = 'http'
    callback_url = '%s://%s/__%s/callback' % (protocol, host, service)
    return callback_url


def get_cloud_site_folder_for_bucket(bucket):
    if not bucket:
        return
    site_configs = get_bucket_site_configs(bucket)
    cloud_site_folder = get_value_from_data(site_configs, "cloud_site_folder") or ""
    cloud_site_folder = smart_unicode(cloud_site_folder).strip("/").strip()
    if not cloud_site_folder:
        cloud_site_folder = bucket
    if "/" in cloud_site_folder or "\\" in cloud_site_folder:
        # 不允许 / 这些出现
        cloud_site_folder = bucket
    return cloud_site_folder
