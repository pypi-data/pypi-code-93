import glob
import ntpath

class DirectoryScanner:

    def __init__(self, **kwargs):
        self.directory = kwargs['directory']
        self.extension = kwargs['extension']

    def get_files(self):
        paths = glob.glob(f'{self.directory}/*{self.extension}')
        sorted_paths = self.sort_files(paths)
        return sorted_paths

    def sort_files(self, paths):
        return sorted(paths, key=self.__splice_file)

    def __splice_file(self, file):
        try:
            return int(ntpath.basename(file).split(self.extension)[0])
        except:
            return ntpath.basename(file).split(self.extension)[0]
