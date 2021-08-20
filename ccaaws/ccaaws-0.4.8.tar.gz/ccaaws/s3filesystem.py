"""S3 filesystem object."""

import os

import ccalogging

from ccaaws.botosession import BotoSession

log = ccalogging.log


class S3FileSystem(BotoSession):
    """Class to mimic filesystem tools with S3."""

    def __init__(self, **kwargs):
        """Connect to AWS S3.

        Optional:
            region: region name
            profile: profile name
        """
        super().__init__(**kwargs)
        self.newClient("s3")
        self.bucket = None

    def getBuckets(self):
        try:
            resp = self.client.list_buckets()
            buckets = resp["Buckets"]
            return buckets
        except KeyError as e:
            log.error(f"Failed to retrieve the bucket list: {e}")

    def xls(self, path, page_size=None):
        if path == "":
            return [[], []]
        paginator = self.client.get_paginator("list_objects")
        paging_args = {
            "Bucket": self.bucket,
            "Prefix": path,
            "Delimiter": "/",
            "PaginationConfig": {"PageSize": page_size},
        }
        iterator = paginator.paginate(**paging_args)
        objs = []
        paths = []
        for resp in iterator:
            # print(resp)
            xpaths = resp.get("CommonPrefixes", [])
            xobjs = resp.get("Contents", [])
            for xobj in xobjs:
                objs.append(xobj)
            for xpath in xpaths:
                paths.append(xpath)
        return [objs, paths]

    def xcp(self, src, dest):
        """Copy to/from S3.

        Args:
            src: source path
            dest: destination path
        """
        if src.startswith("s3://"):
            ret = self._cpFromS3(src, dest)
        else:
            ret = self._cpToS3(src, dest)
        return ret

    def _cpFromS3(self, src, dest):
        """Copy from S3.

        Args:
            src: source path
            dest: destination path
        """
        ret = False
        scheme, bucket, path = self.parseS3Uri(src)
        self.bucket = bucket
        objs, paths = self.xls(path)
        sz = len(objs)
        if sz == 1:
            try:
                # path="/{}".format(path)
                log.debug(f"copying {bucket} {path} to {dest}")
                self.resource.meta.client.download_file(bucket, path, dest)
                ret = True
            except Exception as E:
                log.warning(f"failed to copy file {src} to {dest}, exception was: {E}")
        elif sz == 0:
            log.warning(f"source file not found in s3 {src}")
        else:
            log.warning(f"more than one object returned for {src}. Objects: {objs}")
        return ret

    def _cpToS3(self, src, dest):
        """Copies src to s3://dest.

        Args:
            src: the source path
            dest: the destination path
        """
        ret = False
        if os.path.isfile(src):
            scheme, bucket, path = self.parseS3Uri(dest)
            try:
                self.resource.meta.client.upload_file(src, bucket, path)
                ret = True
            except Exception as E:
                log.warning(f"failed to copy file {src} to {dest}, exception was: {E}")
        else:
            log.warning(f"source file not found {src}")
        return ret

    def parseS3Uri(self, uri):
        """Parses S3 uris.

        s3://bucketname/some/path/some.file
        or
        http(s)://bucketname.s3.amazonaws.com/some/path/some.file

        into a tuple of scheme, bucket and path

        Args:
            uri: the uri to parse
        """
        path = ""
        scheme, bucket = self.parseBucket(uri)
        lscheme = len(scheme)
        if lscheme > 0:
            slashpos = uri.find("/", lscheme + 3)
            if slashpos > -1:
                path = uri[slashpos + 1 :]
        return [scheme, bucket, path]

    def parseScheme(self, uri):
        """Returns the scheme from the supplied uri.

        Args:
            uri: the fully qualified path
                 s3://bucket/file/name
                 https://s3.amazonaws.com/bucket/file/name
        """
        scheme = ""
        schemepos = uri.find("://")
        if schemepos > -1:
            scheme = uri[:schemepos]
        return scheme

    def parseBucket(self, uri):
        """Returns the bucket part of the supplied uri.

        Args:
            uri: the fully qualified path
                 s3://bucket/file/name
                 https://s3.amazonaws.com/bucket/file/name
        """
        bucket = ""
        scheme = self.parseScheme(uri)
        lscheme = len(scheme)
        if lscheme > 0:
            bucketpos = lscheme + 3
            if scheme.startswith("http"):
                dotpos = uri.find(".")
                if dotpos > -1:
                    bucket = uri[bucketpos:dotpos]
            else:
                # s3:// uri
                slashpos = uri.find("/", bucketpos)
                if slashpos > -1:
                    bucket = uri[bucketpos:slashpos]
                else:
                    # just a bucket name, then, with no trailing path
                    bucket = uri[bucketpos:]
        return [scheme, bucket]
