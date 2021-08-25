import gzip


class GzipCompressMixin:
    def gzip_compression_enabled(self):
        return False

    def gzip_gzip_compresslevel(self):
        return 9

    def get_filepaths_to_gzip(self):
        return []

    def make_gzip_outfilepath(self, sourcepath):
        return f'{sourcepath}.gz'

    def gzip_compress_file(self, sourcepath):
        gzip_outfilepath = self.make_gzip_outfilepath(sourcepath)
        sourcecode = open(sourcepath, 'rb').read()
        gzipped_data = gzip.compress(sourcecode, compresslevel=self.gzip_gzip_compresslevel())
        open(gzip_outfilepath, 'wb').write(gzipped_data)
        self.add_deferred_success(f'GZIP compressed {sourcepath} -> {gzip_outfilepath}.')

    def gzip_compress_files(self):
        if not self.gzip_compression_enabled():
            return
        for filepath in self.get_filepaths_to_gzip():
            self.gzip_compress_file(sourcepath=filepath)
