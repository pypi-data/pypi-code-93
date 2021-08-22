# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['plotly_chart_generator',
 'plotly_chart_generator.chart_styles',
 'plotly_chart_generator.subplots',
 'plotly_chart_generator.utils']

package_data = \
{'': ['*']}

install_requires = \
['pandas>=1.0.3,<2.0.0', 'plotly>=4.6.0,<5.0.0', 'seaborn>=0.10.0,<0.11.0']

setup_kwargs = {
    'name': 'plotly-chart-generator',
    'version': '0.3.0',
    'description': 'Quickly display basic Plotly charts based on data inside a Pandas dataframe.',
    'long_description': "======================\nPlotly Chart Generator\n======================\n.. image:: https://img.shields.io/pypi/l/plotly_chart_generator   :alt: PyPI - License\n\nDescription\n-----------\nThis package allows the user to quickly generate plotly charts with customized\nstyling and formatting from Pandas dataframes and other data structures with as\nlittle as one line of code.\n\nThe following chart types can be created:\n\n* Bar charts (from dataframe)\n* Line charts (from dataframe)\n* Scatter charts (from dictionary)\n* Pie charts (from lists, numpy arrays, Pandas series)\n* Histograms (from lists, numpy arrays, Pandas series)\n* Dot charts (from dataframe)\n* Box charts (from lists, numpy arrays, Pandas series)\n* Sunburst charts (from lists, numpy arrays, Pandas series)\n* Scatter charts subplots (from dictionary)\n* Pie chats subplots (from dictionary)\n\nChart examples are available at https://github.com/PrebenHesvik/Plotly-Chart-Generator\n\n\nInstallation\n------------\n\n.. code:: python\n\n    pip install plotly_chart_generator\n\nUsage\n-----\n.. code:: python\n\n    from plotly_chart_generator import PlotlyChart\n    chart = PlotlyChart()\n\n    # create data\n    index = ['Product A', 'Product B', 'Product C']\n    values = {'Products': [37.5, 40.2, 27.8]}\n    data = pd.DataFrame(data=values, index=index).transpose()\n\n\n    # create chart\n    color_palette = chart.color_palette()\n\n    layout = chart.layout(color_palette=color_palette, width=500, height=400,\n                        title='Sales per product (millions)',\n                        title_size=16, xaxis_ticksize=14)\n\n    chart.bar(data, layout=layout, orientation='v', sort_by='Products',\n                ascending=False, bar_width=0.4, textpos='inside', linewidth=1)\n\nDisclaimer\n----------\nMost of the descriptions of arguments have been copied form the Plotly Figure\nReference Guide at https://plotly.com/python/reference/",
    'author': 'Preben Hesvik',
    'author_email': 'Prebenhesvik@hotmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/PrebenHesvik/plotly_chart_builder',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
