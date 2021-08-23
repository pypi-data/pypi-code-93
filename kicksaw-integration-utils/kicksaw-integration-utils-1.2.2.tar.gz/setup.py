# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['kicksaw_integration_utils', 'kicksaw_integration_utils.integrations']

package_data = \
{'': ['*']}

install_requires = \
['boto3>=1.17.3,<2.0.0', 'simple-salesforce>=1.10.1,<2.0.0']

setup_kwargs = {
    'name': 'kicksaw-integration-utils',
    'version': '1.2.2',
    'description': 'A set of helper functions for CSV to Salesforce procedures, with reporting in AWS S3',
    'long_description': '# Overview\n\nA set of helper functions for CSV to Salesforce procedures, with reporting in AWS S3.\nThe use case is extremely specific, but the helpers should be modular so they can be cherry-picked.\n\nTypical use case:\n\n- Receive an S3 event\n- Download the S3 object\n- Serialize the file into JSON\n- Bulk upsert the JSON data to Salesforce\n- Parse the results of the upsert for errors\n- Construct a CSV error report\n- Move the triggering S3 object to an archive folder\n- Push the error report to an error folder in the same bucket\n- Push an object to Salesforce that details information about the above execution\n\n2nd typical use case:\n\n- Start an AWS Step Function\n- Pass the payload to the KicksawSalesforce client and create an execution object, recording this payload\n- upsert a bunch of data, parsing the responses\n- if any errors, push error objects into salesforce, chidling them to the execution object above\n\n# High-level Example\n\nUsing the `Orchestrator` class, you can skip manually setting up a lot of the above\nsteps. This class is intended to be subclassed, and should provide plenty of options\nfor overriding methods to better suit your use-case.\n\n## Inheriting the Orchestrator\n\n```python\n# orchestrator.py\nfrom kicksaw_integration_utils.classes import Orchestrator as BaseOrchestrator\n\n\nclass Orchestrator(BaseOrchestrator):\n    def __init__(self, *args, **kwargs) -> None:\n        super().__init__(*args, **kwargs)\n        # This must be defined in the child class because your Salesforce object could be named anything\n        self.execution_object_name = "Integration_Execution__c"\n\n    @property\n    def execution_sfdc_hash(self):\n        # And it could have any number of fields\n        return {\n            "Number_of_Errors__c": self.error_count,\n            "Error_Report__c": self.error_report_link,\n            "Data_File__c": self.s3_object_key,\n        }\n\n    @property\n    def error_report_link(self):\n        return f"https://{self.bucket_name}.{settings.AWS_REGION}.amazonaws.com/{self.error_file_s3_key}"\n```\n\n## Using the Orchestrator\n\n```python\n# biz_logic.py\nfrom kicksaw_integration_utils.classes import SfClient\n\n# import the custom Orchestrator defined above\nfrom .orchestrator import Orchestrator\n\nsalesforce = SfClient()\norchestrator = Orchestrator("some/s3/key/file.csv", settings.S3_BUCKET, sf_client=salesforce)\n\nupsert_key = "My_External_ID__c"\naccounts_data = [{"Name": "A name", upsert_key: "123"}]\nresults = salesforce.bulk.Account.upsert(results, upsert_key)\n\n# You\'ll call log_batch for each batch you upload. This method\n# will parse the results in search of errors\norchestrator.log_batch(results, accounts_data, "Account", upsert_key)\n\n# This will create the error report, archive the source s3 file, and push\n# the integration object to Salesforce. You\'ll definitely want to customize\n# this by overriding this method or the methods it invokes\norchestrator.automagically_finish_up()\n```\n\n# Low-level Example\n\n```python\nfrom kicksaw_integration_utils.csv_helpers import create_error_report\nfrom kicksaw_integration_utils.s3_helpers import download_file, respond_to_s3_event, upload_file\nfrom kicksaw_integration_utils.sfdc_helpers import extract_errors_from_results\n\n\n# handler for listening to s3 events\ndef handler(event, context):\n    respond_to_s3_event(event, download_and_process)\n\n\ndef download_and_process(s3_object_key, bucket_name):\n    download_path = download_file(s3_object_key, bucket_name)\n\n    # This function contains your own biz logic; does not come from this library\n    results = serialize_and_push_to_sfdc(download_path)\n\n    sucesses, errors = parse_bulk_upsert_results(results)\n\n    report_path, errors_count = create_error_report([errors])\n\n    upload_file(report_path, bucket_name)\n```\n\nJust take what\'cha need!\n\n# Integration app example\n\nTo use Kicksaw\'s integration app, install this package (insert package link here) in your Salesforce organization.\n\nOnce your org is ready to-go, instantiate the `KicksawSalesforce` class and operate like normal, but note:\n\n- Instantiating the client creates an execution object in Salesforce, unless you pass it the id of an already existing execution object\n- All of your bulk operations will have their errors parsed and error objects created in Salesforce if applicable.\n\nFor code examples, please refer to `tests/test_integrations.py`.\n',
    'author': 'Alex Drozd',
    'author_email': 'drozdster@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Kicksaw-Consulting/kicksaw-integration-utils',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
