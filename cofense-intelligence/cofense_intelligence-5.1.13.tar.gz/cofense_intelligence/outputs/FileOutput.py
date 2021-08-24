import os
from cofense_intelligence.output import CofenseIntegration


class FileOutput(CofenseIntegration):
    """
    Parent class for "generic" PhishMe Intelligence integrations; extends :class:`phishme_intelligence.output.base_integration.CofenseIntegration`
    """

    def __init__(self, config, **kwargs):
        super(FileOutput, self).__init__(config, **kwargs)

        if not self.config.get('BASE_DIR'):
            self.config['BASE_DIR'] = os.path.abspath(os.path.dirname(__file__))

    def prep(self):
        pass

    def process(self, mrti):
        output_file = self.get_file_path(mrti)

        self.write_file(mrti, output_file)

    def verify_dirs(self, year_month_day):

        output_path = os.path.join(self.config['BASE_DIR'], 'output/' + year_month_day)

        if not os.path.exists(output_path):
            os.makedirs(output_path)

        return output_path

    def verify_append_dirs(self):
        output_path = os.path.join(self.config['BASE_DIR'], 'output')

        if not os.path.exists(output_path):
            os.makedirs(output_path)

        return output_path

    def get_file_path(self, mrti):
        pass

    def write_file(self, mrti, output_file):
        pass
