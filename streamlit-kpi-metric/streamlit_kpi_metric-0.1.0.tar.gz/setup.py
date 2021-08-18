# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['streamlit_kpi_metric']

package_data = \
{'': ['*']}

install_requires = \
['streamlit>=0.86.0,<0.87.0']

setup_kwargs = {
    'name': 'streamlit-kpi-metric',
    'version': '0.1.0',
    'description': 'Library to create KPI metric for streamlit dashboards',
    'long_description': '## What?\n\n`streamlit-kpi-metric` library function is to facilitate display of key-point indicators to dashboards.\n\n---\n\n## WHY?\n\n- Effective KPIs are important metrics to make sure that you can summerize and pay attention to important indicators.\n  \n- Library makes it easy to generate KPI with different labels to mention important figures.\n\n---\n\n## HOW?\n    \n- ### Install library to respective project\'s `pyproject.toml`\n\n```zsh\npoetry add streamlit-kpi-metrics\n```\n\n- ### Importing function to parsing scripts\n\n```python\nfrom streamlit_kpi_metrics import metric, metric_row\n```\n\n - ### Implementing function\n  Write following code to a file `main.py`\n\n```python\nst.write("## Solo Metric")\nmetric("Metric 0", 150)\n\nst.write("## Multiple Metric")\nmetric_row(\n    {\n        "Metric 1": 10,\n        "Metric 2": 20,\n        "Metric 3": 30,\n        "Metric 4": 40,\n        "Metric 5": 50,\n    }\n)\n```\n\n- ### Running file \n\n```zsh \npoetry run streamlit run main.py\n```\n\n--- \n\n- ### Output of the mentioned code \n![](./static/streamlit-metric-image.png)\n\n---',
    'author': '100mi',
    'author_email': 'smtrgupta96@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
