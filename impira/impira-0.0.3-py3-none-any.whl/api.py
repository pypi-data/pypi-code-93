import json
import os
from pydantic import BaseModel, validate_arguments
import requests
from typing import List, Optional
from urllib.parse import urlparse

class FilePath(BaseModel):
    name: str
    path: str

class InvalidRequest(Exception):
    pass

class APIError(Exception):
    def __init__(self, response):
        self.response = response

    def __str__(self):
        return '%s: %s' % (self.response.status_code, self.response.content)

class IQLError(Exception):
    pass

class Impira:
    def __init__(self, org_name, api_token, base_url='https://app.impira.com'):
        self.org_url = os.path.join(base_url, 'o', org_name)
        self.api_url = os.path.join(self.org_url, 'api/v2')
        self.headers={'X-Access-Token': api_token}

    @validate_arguments
    def upload_files(self, collection_id: str, files: List[FilePath]):
        local_files = len([f for f in files if urlparse(f.path).scheme in ('', 'file')])
        if local_files > 0 and local_files != len(files):
                raise InvalidRequest("All files must be local or URLs, but not a mix (%d/%d were local)" % (local_files, len(files)))
        elif local_files > 0:
            return self._upload_multipart(collection_id, files)
        else:
            return self._upload_url(collection_id, files)

    @validate_arguments
    def get_collection_uid(self, collection_name: str):
        resp = self.query('@__system::collections[uid] Name="%s"' % (collection_name))['data']
        if len(resp) == 0:
            return None

        uids = [x['uid'] for x in resp]
        if len(uids) > 1:
            raise InvalidRequest("Found multiple collections with name '%s': %s" % (collection_name, ', '.join(uids)))

        return uids[0]

    @validate_arguments
    def poll_for_results(self, collection_id: str, uids: List[str]=None):
        uid_filter = 'and in(uid, %s)' % (', '.join(['"%s"' % u for u in uids])) if uids else ''
        query = '''
        @`file_collections::%s`
            File.IsPreprocessed=true and __system.IsProcessed=true
            %s
            [.: __resolve(.)]''' % (collection_id, uid_filter)

        cursor = None

        must_see = set(uids)
        while True:
            resp = self.query(query, mode='poll', cursor=cursor, timeout=60)
            for d in (resp['data'] or []):
                if d['action'] != 'insert':
                    continue
                yield d['data']

                uid = d['data']['uid']
                if len(must_see) > 0:
                    assert uid in must_see, "Broken uid filter (%s not in %s)" % (uid, must_see)
                    must_see.remove(uid)

            cursor = resp['cursor']

            if len(must_see) == 0:
                break

    @validate_arguments
    def query(self, query: str, mode: str="iql", cursor: str=None, timeout: str=None):
        args = {'query': query}
        if cursor is not None:
            args['cursor'] = cursor

        if timeout is not None:
            args['timeout'] = timeout

        resp = requests.post(os.path.join(self.api_url, mode), headers=self.headers, json={'query': query})
        if not resp.ok:
            raise APIError(resp)

        d = resp.json()
        if 'error' in d and d['error'] is not None:
            raise IQLError(d['error'])

        return resp.json()

    @validate_arguments
    def _upload_multipart(self, collection_id: str, files: List[FilePath]):
        files_body = [t for f in files for t in \
                [('file', open(f.path, 'rb')), ('data', json.dumps({'File': {'name': f.name}}))]]
        resp = requests.post(self._build_collection_url(collection_id, use_async=True), headers=self.headers,
                files=tuple(files_body))
        if not resp.ok:
            raise APIError(resp)

        return resp.json()['uids']

    @validate_arguments
    def _upload_url(self, collection_id: str, files: List[FilePath]):
        resp = requests.post(self._build_collection_url(collection_id, use_async=True), headers=self.headers,
                json={'data': [{'File': {'name': f.name, 'path': f.path}} for f in files]})
        if not resp.ok:
            raise APIError(resp)

        return resp.json()['uids']

    @validate_arguments
    def _build_collection_url(self, collection_id: str, use_async=False):
        base_url = os.path.join(self.api_url, 'fc', collection_id)
        if use_async:
            base_url = base_url + '?async=1'
        return base_url


