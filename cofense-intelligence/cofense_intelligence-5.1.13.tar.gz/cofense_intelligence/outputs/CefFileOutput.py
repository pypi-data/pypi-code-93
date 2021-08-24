import re,os
from datetime import datetime
from .FileOutput import FileOutput


class CefFileOutput(FileOutput):

    def get_file_path(self, mrti):
        first_published = re.search('deviceCustomDate1=(\d+)', mrti).group(1)
        year_month_day = datetime.fromtimestamp(int(first_published) / 1e3).strftime('%Y-%m-%d')

        output_path = self.verify_append_dirs()
        output_file = os.path.join(output_path, year_month_day + '.cef')

        return output_file

    def write_file(self, mrti, output_file):
        with open(output_file, 'ab') as outfile:
            outfile.write(mrti.encode('utf-8') + b'\n')
