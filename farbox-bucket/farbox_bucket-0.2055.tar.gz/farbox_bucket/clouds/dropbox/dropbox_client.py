#coding: utf8
import dropbox
from dropbox.files import FileMetadata, FolderMetadata, DeletedMetadata
from dropbox.exceptions import ApiError, InternalServerError, AuthError

from farbox_bucket.settings import sentry_client, MAX_FILE_SIZE
from farbox_bucket.utils import string_types
from farbox_bucket.utils.functional import curry, cached_property
from farbox_bucket.utils.path import is_a_hidden_path


from farbox_bucket.server.helpers.file_manager import sync_file_by_server_side

from farbox_bucket.utils import get_value_from_data, smart_str
from farbox_bucket.clouds.utils import get_cloud_site_folder_for_bucket
from farbox_bucket.clouds.dropbox.utils import get_dropbox_cursor, set_dropbox_cursor
from farbox_bucket.clouds.dropbox.dropbox_auth_token import get_dropbox_account, update_dropbox_account, \
    Dropbox_APP_SECRET, Dropbox_APP_KEY, has_dropbox_account, get_buckets_from_dropbox_account_id


class DropboxClient(object):

    def __init__(self, account_id=None, bucket=None):
        self.account_id = account_id
        self.bucket = bucket

        self.account_data = get_dropbox_account(dropbox_account_id=account_id, bucket=bucket) or {}
        if not self.account_id:
            self.account_id = self.account_data.get("account_id")

        self.refresh_token = self.account_data.get("refresh_token")
        self.access_token  = self.account_data.get("access_token")

        self.client = None

    @cached_property
    def cloud_site_folder(self):
        return get_cloud_site_folder_for_bucket(self.bucket)


    def capture_error(self):
        if sentry_client:
            try: sentry_client.captureException()
            except: pass


    def get_client(self):
        if self.client is None and self.access_token:
            self.client = dropbox.Dropbox(app_key=Dropbox_APP_KEY,
                            app_secret=Dropbox_APP_SECRET,
                            oauth2_access_token=self.access_token,
                            oauth2_refresh_token=self.refresh_token)
        return self.client


    def auto_update_token(self):
        if not self.client or not isinstance(self.client, dropbox.Dropbox):
            return
        new_access_token = self.client._oauth2_access_token
        new_expires_at = self.client._oauth2_access_token_expiration
        if new_access_token and new_access_token != self.access_token:
            update_dropbox_account(dropbox_account_id=self.account_id,
                                   bucket=self.bucket,
                                   access_token=new_access_token,
                                   expires_at=new_expires_at)

    def get_all_files_by_path(self, path):
        # 一般是获得某个site_folder下的所有文件信息
        path = '/'+path.lstrip('/')
        return self.get_files(no_cursor=True, return_cursor=False, path=path)

    def get_files(self, no_cursor=False, return_cursor=False, path=None):
        if path is None:
            path = self.cloud_site_folder or ""
        if path and not path.startswith("/"):
            path = "/%s" % path
        try:
            return self.do_get_files(no_cursor=no_cursor, return_cursor=return_cursor, path=path)
        except AuthError as error:
            # clear the long-live refresh_token
            update_dropbox_account(self.account_id, self.bucket, refresh_token="")
        except:
            self.capture_error()
        if return_cursor:
            return [], ""
        else:
            return []

    def do_get_files(self, no_cursor=False, return_cursor=True, path=''):
        # 遍历所有文件, 默认会寻址 cursor，即获得最新的变更的文件
        client = self.get_client()
        if not client or not isinstance(client, dropbox.Dropbox):
            return

        def files_gainer(files=None, cursor=None):
            files = files or []
            try:
                if cursor:
                    result = client.files_list_folder_continue(cursor)
                else:
                    result = client.files_list_folder(path=path, recursive=True, include_deleted=True)
                new_cursor = result.cursor
                files += result.entries
                if new_cursor == cursor or not result.has_more: # 前者表示未更新，后者表示有更多的内容
                    return files, new_cursor
                else:
                    return files_gainer(files, new_cursor) # loop
            except ApiError as e:
                error_info = get_value_from_data(e.error, 'error')
                if isinstance(error_info, dict):
                    error_tag = error_info.get('.tag')
                    if error_tag in ['not_found']:
                        return [], cursor
                raise e
            except Exception as e:
                raise e

        if no_cursor:
            default_cursor = None
        else:
            default_cursor = get_dropbox_cursor(self.account_id, bucket=self.bucket)
            #if not default_cursor:
            #    c = client.files_list_folder_get_latest_cursor(path=path, recursive=True, include_deleted=True)
            #    default_cursor = c.cursor
                #set_dropbox_cursor(self.account_id, default_cursor)

        files, cursor = files_gainer(cursor=default_cursor)

        files_to_return = []

        for f in files:
            f_info = {}
            path = f.path_display.lstrip('/')
            version2 = getattr(f, 'rev', None)
            if isinstance(f, DeletedMetadata):
                f_info = {'path': path, 'is_deleted': True}
            elif isinstance(f, FileMetadata):
                f_info = {
                    'path': path,
                    'mtime': f.client_modified, # 客户端的最后修改时间
                    'smtime': f.server_modified, # 服务端的最后修改时间
                    'file_id': f.id,
                    'is_dir': False,
                    'size': f.size,
                    'version2': version2,
                }
            elif isinstance(f, FolderMetadata):
                f_info = {
                    'path': path,
                    'is_dir': True
                }
            if f_info:
                if not path.count('/') and not f_info.get('is_dir'): # 根目录的非folder类型不处理
                    continue
                files_to_return.append(f_info)

        if return_cursor and cursor and cursor != default_cursor:
            # 保留 cursor，下次抓取文件就不用特别处理了
            # set_dropbox_cursor(self.account_id, cursor=cursor)
            return files_to_return, cursor
        else:
            return files_to_return

    def get_file(self, filepath, just_content=True):
        # 得到文件的原始内容
        #filepath = filepath.lower()
        if not filepath.startswith('/'):
            filepath = '/%s'%filepath
        client = self.get_client()
        if not client or not isinstance(client, dropbox.Dropbox):
            return
        meta, res = client.files_download(filepath) # todo 404 的问题
        if just_content:
            return res.content
        else:
            return meta, res


    def create_file(self, filepath, raw_content):
        if not filepath.startswith('/'):
            filepath = '/%s'%filepath
        client = self.get_client()
        if not client or not isinstance(client, dropbox.Dropbox):
            return
        try:
            response = client.files_upload(smart_str(raw_content), filepath, mode=dropbox.files.WriteMode.overwrite)
            return response
        except InternalServerError:
            # dropbox 自己的问题
            return
        except ApiError: # 比如 disallowed_name， 不允许的名字
            return
        except:
            self.capture_error()


    def create_folder(self, path):
        if not path.startswith('/'):
            path = '/%s' % path
        client = self.get_client()
        if not client or not isinstance(client, dropbox.Dropbox):
            return
        try:
            folder_meta = self.client.files_get_metadata(path)
        except:
            # 不存在，尝试创建
            try: client.files_create_folder_v2(path)
            except: pass


    def create_site_folder(self):
        if self.cloud_site_folder:
            self.create_folder(self.cloud_site_folder)


    def delete_file(self, filepath):
        # /(.|[\r\n])*  -> path 要符合这个规则
        filepath = '/' + filepath.strip('/') # 必须 / 开头
        client = self.get_client()
        if not client or not isinstance(client, dropbox.Dropbox):
            return # ignore
        try:
            client.files_delete_v2(filepath)
        except:
            # 可能已经不存在了
            pass


    ################ sync related starts #########

    def sync(self):
        if not self.bucket:
            return
        try:
            file_metas, new_cursor = self.get_files(return_cursor=True, path=self.cloud_site_folder)
            self.sync_filepath_metas(file_metas)
            if new_cursor:
                # 同步成功后，保存 cursor
                set_dropbox_cursor(self.account_id, bucket=self.bucket, cursor=new_cursor)
        except:
            self.capture_error()


    def sync_under_path(self, path):
        # 这个是全遍历某个path, 不会记录cursor
        if not self.bucket:
            return
        if not path or not isinstance(path, string_types):
            return
        path = path.strip()
        try:
            file_metas = self.get_all_files_by_path(path)
            return self.sync_filepath_metas(file_metas)
        except:
            self.capture_error()


    def sync_filepath_meta(self, filepath_meta):
        if not filepath_meta or not isinstance(filepath_meta, dict):
            return
        if not self.bucket or not self.cloud_site_folder:
            return
        is_dir = filepath_meta.get("is_dir", False)
        is_deleted = filepath_meta.get("is_deleted", False)
        file_size = filepath_meta.get("size", 0)
        version2 = filepath_meta.get("version2")
        path = filepath_meta.get("path", "").lstrip("/")
        prefix = self.cloud_site_folder+"/"
        if not path.startswith(prefix):
            return
        if file_size > MAX_FILE_SIZE/2: # 25 MB，尽可能避免 Dropbox 1:1 存储备份情况的出现
            return
        relative_path = path.replace(prefix, "", 1).lstrip("/")
        if not relative_path:
            return
        if is_a_hidden_path(relative_path):
            return

        get_content_func = curry(self.get_file, path, just_content=True)

        sync_file_by_server_side(self.bucket, relative_path, content=get_content_func,
                                 version2=version2, is_dir=is_dir, is_deleted=is_deleted, client="dropbox")


    def sync_filepath_metas(self, file_metas):
        for file_meta in file_metas:
            self.sync_filepath_meta(file_meta)


    ################ sync related ends #########





def sync_by_dropbox_client(dropbox_account_id):
    if not has_dropbox_account(dropbox_account_id):
        return
    buckets = get_buckets_from_dropbox_account_id(dropbox_account_id)
    for bucket in buckets:
        dropbox_client = DropboxClient(account_id=dropbox_account_id, bucket=bucket)
        dropbox_client.sync()






