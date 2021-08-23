import os

from requests_futures.sessions import FuturesSession

from savvihub.api.file_object import DownloadableFileObject
from savvihub.common.utils import wait_all_futures


class Downloader:
    @classmethod
    def download(cls, local_path, file, progressable=None):
        dirname = os.path.dirname(local_path)
        basename = os.path.basename(local_path)
        d = DownloadableFileObject(file.download_url.url, dirname, basename)
        d.download(progressable=progressable)

    @classmethod
    def bulk_download(cls, local_base_path, remote_files, progressable=None):
        if len(remote_files) <= 0:
            return
        session = FuturesSession(max_workers=os.environ.get('SAVVIHUB_PARALLEL', 20))
        futures = []
        for remote_file in remote_files:
            if remote_file.path.endswith('/'):
                continue

            d = DownloadableFileObject(remote_file.download_url.url, local_base_path, remote_file.path)
            futures.append(d.download(session, progressable=progressable))

        wait_all_futures(futures)