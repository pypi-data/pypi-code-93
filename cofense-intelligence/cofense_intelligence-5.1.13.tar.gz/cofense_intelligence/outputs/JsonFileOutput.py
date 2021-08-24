import json, os
from datetime import datetime
from .FileOutput import FileOutput

class JsonFileOutput(FileOutput):

    def get_file_path(self, mrti):
        year_month_date = datetime.fromtimestamp(mrti.first_published / 1e3).strftime('%Y-%m-%d')

        output_path = self.verify_dirs(year_month_date)

        output_file = os.path.join(output_path, str(mrti.threat_id) + '.json')

        return output_file

    def write_file(self, mrti, output_file):
        with open(output_file, 'w') as outfile:
            outfile.write(json.dumps(mrti.json))
