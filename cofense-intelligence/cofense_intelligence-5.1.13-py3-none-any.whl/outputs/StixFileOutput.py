import re,os
from .FileOutput import FileOutput
import defusedxml.ElementTree as etree


class StixFileOutput(FileOutput):

    def get_file_path(self, mrti):
        threat_id = re.search('<campaign:Title>(\d+)</campaign:Title>', mrti).group(1)
        year_month_day = re.search('<indicator:Start_Time precision=\"second\">(\d{4}-\d{2}-\d{2})T', mrti).group(1)

        output_path = self.verify_dirs(year_month_day)
        output_file = os.path.join(output_path, threat_id + '.stix')

        return output_file

    def write_file(self, mrti, output_file):
        threat_id = re.search('<campaign:Title>(\d+)</campaign:Title>', mrti).group(1)

        try:
            stix_xml = etree.fromstring(mrti.encode('utf-8'))
        except etree.XMLSyntaxError:
            raise RuntimeError('XML parsing error of STIX package for threat report: ' + threat_id)

        with open(output_file, 'wb') as outfile:
            outfile.write(mrti.encode('utf-8'))
