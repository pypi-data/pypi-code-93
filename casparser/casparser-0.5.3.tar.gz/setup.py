# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['casparser', 'casparser.analysis', 'casparser.parsers', 'casparser.process']

package_data = \
{'': ['*']}

install_requires = \
['casparser-isin>=2021.7.21',
 'click>=8.0.1,<9.0.0',
 'colorama>=0.4.4,<0.5.0',
 'pdfminer.six==20201018',
 'python-dateutil>=2.8.1,<3.0.0',
 'rich>=10.1.0,<11.0.0',
 'typing-extensions>=3.10,<4.0']

extras_require = \
{'mupdf': ['PyMuPDF>=1.18.14,<2.0.0']}

entry_points = \
{'console_scripts': ['casparser = casparser.cli:cli']}

setup_kwargs = {
    'name': 'casparser',
    'version': '0.5.3',
    'description': '(Karvy/Kfintech/CAMS) Consolidated Account Statement (CAS) PDF parser',
    'long_description': '# CASParser\n\n[![code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)\n[![GitHub](https://img.shields.io/github/license/codereverser/casparser)](https://github.com/codereverser/casparser/blob/main/LICENSE)\n![GitHub Workflow Status](https://img.shields.io/github/workflow/status/codereverser/casparser/run-tests)\n[![codecov](https://codecov.io/gh/codereverser/casparser/branch/main/graph/badge.svg?token=DYZ7TXWRGI)](https://codecov.io/gh/codereverser/casparser)\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/casparser)\n\nParse Consolidated Account Statement (CAS) PDF files generated from CAMS/KFINTECH\n\n`casparser` also includes a command line tool with the following analysis tools\n- `summary`- print portfolio summary\n- (**BETA**) `gains` - Print capital gains report (summary and detailed)\n  - with option to generate csv files for ITR in schedule 112A format\n\n\n## Installation\n```bash\npip install -U casparser\n``` \n\n### with faster PyMuPDF parser\n```bash\npip install -U \'casparser[mupdf]\'\n```\n\n**Note:** Enabling this dependency could result in licensing changes. Check the \n[License](#license) section for more details \n \n\n## Usage\n\n```python\nimport casparser\ndata = casparser.read_cas_pdf("/path/to/cas/file.pdf", "password")\n\n# Get data in json format\njson_str = casparser.read_cas_pdf("/path/to/cas/file.pdf", "password", output="json")\n\n# Get transactions data in csv string format\ncsv_str = casparser.read_cas_pdf("/path/to/cas/file.pdf", "password", output="csv")\n\n```\n\n### Data structure\n\n```json\n{\n    "statement_period": {\n        "from": "YYYY-MMM-DD",\n        "to": "YYYY-MMM-DD"\n    },\n    "file_type": "CAMS/KARVY/UNKNOWN",\n    "cas_type": "DETAILED/SUMMARY",\n    "investor_info": {\n        "email": "string",\n        "name": "string",\n        "mobile": "string",\n        "address": "string"\n    },\n    "folios": [\n        {\n            "folio": "string",\n            "amc": "string",\n            "PAN": "string",\n            "KYC": "OK/NOT OK",\n            "PANKYC": "OK/NOT OK",\n            "schemes": [\n                {\n                    "scheme": "string",\n                    "isin": "string",\n                    "amfi": "string",\n                    "advisor": "string",\n                    "rta_code": "string",\n                    "rta": "string",\n                    "open": "number",\n                    "close": "number",\n                    "close_calculated": "number",\n                    "valuation": {\n                      "date": "date",\n                      "nav": "number",\n                      "value": "number"\n                    },\n                    "transactions": [\n                        {\n                            "date": "YYYY-MM-DD",\n                            "description": "string",\n                            "amount": "number",\n                            "units": "number",\n                            "nav": "number",\n                            "balance": "number",\n                            "type": "string",\n                            "dividend_rate": "number"\n                        }\n                    ]\n                }\n            ]\n        }\n    ]\n}\n```\nNotes: \n- Transaction `type` can be any value from the following\n  - `PURCHASE`\n  - `PURCHASE_SIP`\n  - `REDEMPTION`\n  - `SWITCH_IN`\n  - `SWITCH_IN_MERGER`\n  - `SWITCH_OUT`\n  - `SWITCH_OUT_MERGER`\n  - `DIVIDEND_PAYOUT`\n  - `DIVIDEND_REINVESTMENT`\n  - `SEGREGATION`\n  - `STAMP_DUTY_TAX`\n  - `TDS_TAX`\n  - `STT_TAX`\n  - `MISC`\n- `dividend_rate` is applicable only for `DIVIDEND_PAYOUT` and \n  `DIVIDEND_REINVESTMENT` transactions.\n  \n### CLI\n\ncasparser also comes with a command-line interface that prints summary of parsed \nportfolio in a wide variety of formats. \n\n```\nUsage: casparser [-o output_file.json|output_file.csv] [-p password] [-s] [-a] CAS_PDF_FILE\n\n  -o, --output FILE               Output file path. Saves the parsed data as json or csv\n                                  depending on the file extension. For other extensions, the\n                                  summary output is saved. [See note below]\n\n  -s, --summary                   Print Summary of transactions parsed.\n  -p PASSWORD                     CAS password\n  -a, --include-all               Include schemes with zero valuation in the\n                                  summary output\n  -g, --gains                     Generate Capital Gains Report (BETA)\n  --gains-112a ask|FY2020-21      Generate Capital Gains Report - 112A format for\n                                  a given financial year - Use \'ask\' for a prompt \n                                  from available options (BETA)\n  --force-pdfminer                Force PDFMiner parser even if MuPDF is\n                                  detected\n\n  --version                       Show the version and exit.\n  -h, --help                      Show this message and exit.\n``` \n\n#### CLI examples\n```\n# Print portfolio summary\ncasparser /path/to/cas.pdf -p password \n\n# Print portfolio and capital gains summary\ncasparser /path/to/cas.pdf -p password -g\n\n# Save parsed data as a json file\ncasparser /path/to/cas.pdf -p password -o pdf_parsed.json\n\n# Save parsed data as a csv file\ncasparser /path/to/cas.pdf -p password -o pdf_parsed.csv\n\n# Save capital gains transactions in csv files (pdf_parsed-gains-summary.csv and \n# pdf_parsed-gains-detailed.csv)\ncasparser /path/to/cas.pdf -p password -g -o pdf_parsed.csv\n\n```\n\n**Note:** `casparser cli` supports two special output file formats [-o _file.json_ / _file.csv_]\n1. `json` - complete parsed data is exported in json format (including investor info)\n2. `csv` - Summary info is exported in csv format if the input file is a summary statement or if \n   a summary flag (`-s/--summary`) is passed as argument to the CLI. Otherwise, full \n   transaction history is included in the export. \n   If `-g` flag is present, two additional files \'{basename}-gains-summary.csv\', \n   \'{basename}-gains-detailed.csv\' are created with the capital-gains data.\n3. any other extension - The summary table is saved in the file. \n\n\n#### Demo\n\n![demo](https://raw.githubusercontent.com/codereverser/casparser/main/assets/demo.jpg)\n\n## ISIN & AMFI code support\n\nSince v0.4.3, `casparser` includes support for identifying ISIN and AMFI code for the parsed schemes\nvia the helper module [casparser-isin](https://github.com/codereverser/casparser-isin/). If the parser\nfails to assign ISIN or AMFI codes to a scheme, try updating the local ISIN database by \n\n```shell\ncasparser-isin --update\n```\n\nIf it still fails, please raise an issue at [casparser-isin](https://github.com/codereverser/casparser-isin/issues/new) with the \nfailing scheme name(s). \n\n## License\n\nCASParser is distributed under MIT license by default. However enabling the optional dependency\n`mupdf` would imply the use of [PyMuPDF](https://github.com/pymupdf/PyMuPDF) /\n[MuPDF](https://mupdf.com/license.html) and hence the licenses GNU GPL v3 and GNU Affero GPL v3 \nwould apply. Copies of all licenses have been included in this repository. - _IANAL_\n \n## Resources\n1. [CAS from CAMS](https://www.camsonline.com/Investors/Statements/Consolidated-Account-Statement)\n2. [CAS from Karvy/Kfintech](https://mfs.kfintech.com/investor/General/ConsolidatedAccountStatement)\n\n',
    'author': 'Sandeep Somasekharan',
    'author_email': 'codereverser@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/codereverser/casparser',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
