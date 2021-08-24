import yaml
import tempfile
import os 

from .source_code_scanner import SourceCodeScanner
from .exceptions import SourceCodeScannerException


class SCC(SourceCodeScanner):

    def __init__(self, source_code_dir):
        super().__init__(source_code_dir)
        self.__scan_result = {}

    @property
    def repository(self):
        return 'public.ecr.aws/e1z1q7t1/scc'

    @property
    def tag(self):
        return 'latest'

    @property
    def container_source_dir(self):
        bitbucket = os.getenv('BITBUCKET_CLONE_DIR')
        return bitbucket or '/code'

    def _read_scan_stdout(self, stdout_generator):
        with tempfile.TemporaryFile() as yaml_output:
            for chunk in stdout_generator:
                yaml_output.write(chunk)

            yaml_output.seek(0)

            self.__scan_result = yaml.load(
                yaml_output,
                Loader=yaml.FullLoader
            )

    @property
    def summary(self):
        summary = self.__scan_result.get('SUM')
        if not summary:
            raise SourceCodeScannerException(
                'Unexpected error retrienving source code summary metrics'
            )

        return summary

    @property
    def total_source_code_lines(self):
        return self.summary.get('code')

    @property
    def command(self):
        return [
            '--no-cocomo',
            '--no-complexity',
            '--format',
            'cloc-yaml'
        ]
