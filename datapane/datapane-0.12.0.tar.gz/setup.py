# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['datapane',
 'datapane.client',
 'datapane.client.api',
 'datapane.client.api.report',
 'datapane.client.scripts',
 'datapane.common',
 'datapane.resources',
 'datapane.resources.local_report',
 'datapane.resources.report_def',
 'datapane.resources.templates',
 'datapane.resources.templates.report_py',
 'datapane.resources.templates.script',
 'datapane.runner']

package_data = \
{'': ['*'], 'datapane.resources.templates': ['report_ipynb/*']}

install_requires = \
['Jinja2>=2.11.0,<4.0.0',
 'PyYAML>=5.1.0,<6.0.0',
 'altair>=4.0.0,<5.0.0',
 'boltons>=21.0.0,<22.0.0',
 'chardet>=3.0.4,<5.0.0',
 'click-spinner>=0.1.8,<0.2.0',
 'click>=7.1.0,<9.0.0',
 'colorlog>=4.1.0,<7.0.0',
 'dacite>=1.0.2,<2.0.0',
 'datacommons-pandas>=0.0.3,<0.0.4',
 'datacommons>=1.4.3,<2.0.0',
 'dominate>=2.4.0,<3.0.0',
 'furl>=2.0.0,<3.0.0',
 'glom>=20.5.0,<21.0.0',
 'importlib_resources>=5.0.0,<6.0.0',
 'jsonschema>=3.0.0,<4.0.0',
 'lxml>=4.0.0,<5.0.0',
 'micawber>=0.5.0',
 'munch>=2.3.0,<3.0.0',
 'nbconvert>=5.6.1,<7.0.0',
 'packaging>=20.0.0,<22.0.0',
 'pandas>=1.1.0,<2.0.0',
 'posthog>=1.4.1,<2.0.0',
 'pyarrow>=3.0.0,<6.0.0',
 'pydantic>=1.6.0,<2.0.0',
 'requests-toolbelt>=0.9.1,<0.10.0',
 'requests>=2.19.0,<3.0.0',
 'stringcase>=1.2.0,<2.0.0',
 'tabulate>=0.8.0,<0.9.0',
 'toolz>=0.11.0,<0.12.0',
 'validators>=0.17.1',
 'vega-datasets>=0.9.0,<0.10.0']

extras_require = \
{'cloud': ['flit-core>=3.0.0,<3.1.0'],
 'plotting': ['matplotlib>=3.0.0,<4.0.0',
              'plotly>=4.0.0,<6.0.0',
              'bokeh>=2.2.0,<2.3.0',
              'folium>=0.12.0,<0.13.0']}

entry_points = \
{'console_scripts': ['datapane = datapane.client.__main__:main',
                     'dp-runner = datapane.runner.__main__:main']}

setup_kwargs = {
    'name': 'datapane',
    'version': '0.12.0',
    'description': 'Datapane client library and CLI tool',
    'long_description': '<p align="center">\n  <a href="https://datapane.com">\n    <img src="https://datapane.com/static/datapane-logo-dark.png" width="250px" alt="Datapane" />\n  </a>\n</p>\n<p align="center">\n    <a href="https://datapane.com">Datapane Teams</a> |\n    <a href="https://docs.datapane.com">Documentation</a> |\n    <a href="https://datapane.github.io/datapane/">API Docs</a> |\n    <a href="https://docs.datapane.com/changelog">Changelog</a> |\n    <a href="https://twitter.com/datapaneapp">Twitter</a> |\n    <a href="https://blog.datapane.com">Blog</a>\n    <br /><br />\n    <a href="https://pypi.org/project/datapane/">\n        <img src="https://img.shields.io/pypi/dm/datapane?label=pip%20downloads" alt="Pip Downloads" />\n    </a>\n    <a href="https://pypi.org/project/datapane/">\n        <img src="https://img.shields.io/pypi/v/datapane?color=blue" alt="Latest release" />\n    </a>\n    <a href="https://anaconda.org/conda-forge/datapane">\n        <img alt="Conda (channel only)" src="https://img.shields.io/conda/vn/conda-forge/datapane">\n    </a>\n</p>\n<h4>Turn a Python analysis into a beautiful document in 3 lines of code.\n</h1>\n\nDatapane is a Python library which makes it simple to build reports from the common objects in your data analysis, such as pandas DataFrames, plots from Python visualisation libraries, and Markdown.\n\nReports can be exported as standalone HTML documents, with rich components which allow data to be explored and visualisations to be used interactively. You can also publish reports to our free public community platform or share them securely with your team and clients.\n\n# Getting Started\n\n## Installing Datapane\n\nThe best way to install Datapane is through pip or conda.\n\n#### pip\n\n`pip3 install -U datapane`\n\n#### conda\n\n`conda install -c conda-forge "datapane>=0.10.0"`\n\nDatapane also works well in hosted Jupyter environments such as Colab or Binder, where you can install as follows:\n\n`!pip3 install --quiet datapane`\n\n## Explainer Video\n\nhttps://user-images.githubusercontent.com/3541695/117458709-7e80ba80-af42-11eb-9fa7-a11bb05229fe.mp4\n\n## Hello world\n\nLet\'s say you wanted to create a document with a table viewer and an interactive plot:\n\n```python\nimport pandas as pd\nimport altair as alt\nimport datapane as dp\n\ndf = pd.read_csv(\'https://covid.ourworldindata.org/data/vaccinations/vaccinations-by-manufacturer.csv\', parse_dates=[\'date\'])\ndf = df.groupby([\'vaccine\', \'date\'])[\'total_vaccinations\'].sum().reset_index()\n\nplot = alt.Chart(df).mark_area(opacity=0.4, stroke=\'black\').encode(\n    x=\'date:T\',\n    y=alt.Y(\'total_vaccinations:Q\'),\n    color=alt.Color(\'vaccine:N\', scale=alt.Scale(scheme=\'set1\')),\n    tooltip=\'vaccine:N\'\n).interactive().properties(width=\'container\')\n\ntotal_df = df[df["date"] == df["date"].max()].sort_values("total_vaccinations", ascending=False).reset_index(drop=True)\ntotal_styled = total_df.style.bar(subset=["total_vaccinations"], color=\'#5fba7d\', vmax=total_df["total_vaccinations"].sum())\n\ndp.Report("## Vaccination Report",\n    dp.Plot(plot, caption="Vaccinations by manufacturer over time"),\n    dp.Table(total_styled, caption="Current vaccination totals by manufacturer")\n).save(path=\'report.html\', open=True)\n```\n\nThis would package a standalone HTML report document such as the following:\n\n![Report Example](https://user-images.githubusercontent.com/3541695/117442319-82a2dd00-af2e-11eb-843e-29097f425a55.png)\n\n## Text Reports\n\nIf you are writing a report with a lot of text e.g. an article or tutorial, try our [Text Report](https://docs.datapane.com/reports/blocks/text-reports) web editor, where you can combine Markdown with assets uploaded from Python. Here\'s how you\'d do it for the previous example:\n\n```Python\ndp.TextReport("## Vaccination Report",\n    dp.Plot(plot, caption="Vaccinations by manufacturer over time"),\n    dp.Table(total_styled, caption="Current vaccination totals by manufacturer")\n).upload(name="Example vaccination report")\n```\n\nNote that you\'ll need an account on Datapane.com to use TextReports. This will bring up the web editor, where you can add additional commentary to these assets:\n\n<img width="1077" alt="TextReport editor and preview" src="https://user-images.githubusercontent.com/16949044/125301674-1cb64580-e323-11eb-83ea-9b1e1b981734.png">\n\n## Featured Examples\n\nHere a few samples of the top reports created by the Datapane community. To see more, see our [featured](https://datapane.com/featured) section.\n\n- [Tutorial Report](https://datapane.com/u/leo/reports/tutorial-1/) by Datapane Team\n- [Coindesk analysis](https://datapane.com/u/greg/reports/initial-coindesk-article-data/) by Greg Allan\n- [COVID-19 Trends by Quarter](https://datapane.com/u/keith8/reports/covid-19-trends-by-quarter/) by Keith Johnson\n- [Ecommerce Report](https://datapane.com/u/leo/reports/e-commerce-report/) by Leo Anthias\n- [Example Academic Paper](https://datapane.com/u/kalru/reports/supplementary-material/) by Kalvyn Roux\n- [Example Sales Report](https://datapane.com/u/datapane/reports/sample-internal-report/) by Datapane Team\n- [Example Client Report](https://datapane.com/u/datapane/reports/sample-external-report/) by Datapane Team\n- [Exploration of Restaurants in Kyoto](https://datapane.com/u/ryancahildebrandt/reports/kyoto-in-stations-and-restaurants/) by Ryan Hildebrandt\n- [The Numbers on Particles](https://datapane.com/u/ryancahildebrandt/reports/the-numbers-on-particles/) by Ryan Hildebrandt\n\n## Next Steps\n\n- [Read the documentation](https://docs.datapane.com)\n- [Browse the API docs](https://datapane.github.io/datapane/)\n- [Browse samples and demos](https://github.com/datapane/gallery/)\n- [View featured reports](https://datapane.com/explore/?tab=featured)\n\n# Sharing Reports\n\n## Public sharing\n\nIn addition to saving documents locally, you can use [Datapane Community](https://datapane.com/explore) to publish your reports. Datapane Community is a free hosted platform which is used by tens of thousands of people each month to view and share Python reports.\n\n- Reports can be published for free and shared publicly\n- You can embed them into places like Medium, Reddit, or your own website (see [here](https://docs.datapane.com/reports/embedding-reports-in-social-platforms))\n- Viewers can explore and download your data with additional DataTable analysis features\n\nTo get started, create a free API key (see [here](https://docs.datapane.com/tut-getting-started#authentication)) and call the `upload` function on your report,\n\n```python\nr = dp.Report(dp.DataTable(df), dp.Plot(chart))\nr.upload(name="2020 Stock Portfolio", open=True)\n```\n\n## Private sharing\n\nIf you need private report sharing, [Datapane Teams](https://docs.datapane.com/datapane-teams/) allows secure sharing of reports and the ability to deploy your Jupyter Notebooks or Python scripts as interactive apps.\n\n- Share reports privately with your company or external clients\n- Deploy Jupyter Notebooks and scripts as apps, with inputs that can be run by your team interactively to dynamically create results\n- Schedule reports to automatically update\n\nDatapane Teams is offered as both a managed SaaS service and an on-prem install. For more information, see [the documentation](https://docs.datapane.com/datapane-teams/tut-deploying-a-script). You can find pricing [here](https://datapane.com/pricing).\n\n# Analytics\n\nBy default, the Datapane Python library collects error reports and usage telemetry.\nThis is used by us to help make the product better and to fix bugs.\nIf you would like to disable this, simply create a file called `no_analytics` in your `datapane` config directory, e.g.\n\n### Linux\n\n```bash\n$ mkdir -p ~/.config/datapane && touch ~/.config/datapane/no_analytics\n```\n\n### macOS\n\n```bash\n$ mkdir -p ~/Library/Application\\ Data/datapane && touch ~/Library/Application\\ Data/no_analytics\n```\n\n### Windows (PowerShell)\n\n```powershell\nPS> mkdir ~/AppData/Roaming/datapane -ea 0\nPS> ni ~/AppData/Roaming/datapane/no_analytics -ea 0\n```\n\nYou may need to try `~/AppData/Local` instead of `~/AppData/Roaming` on certain Windows configurations depending on the type of your user-account.\n\n# Joining the community\n\nLooking to get answers to questions or engage with us and the wider community? Check out our [GitHub Discussions](https://github.com/datapane/datapane/discussions) board.\n\nSubmit feature requests, issues, and bug reports on this GitHub repo.\n\n## Open-source, not open-contribution\n\nDatapane is currently closed to external code contributions. However, we are tremendously grateful to the community for any feature requests, ideas, discussions, and bug reports.\n',
    'author': 'Datapane Team',
    'author_email': 'dev@datapane.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://www.datapane.com',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7.1,<4.0.0',
}


setup(**setup_kwargs)
