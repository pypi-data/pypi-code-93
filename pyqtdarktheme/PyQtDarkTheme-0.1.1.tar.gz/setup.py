# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['qdarktheme',
 'qdarktheme.Qt',
 'qdarktheme.Qt.QtCore',
 'qdarktheme.Qt.QtGui',
 'qdarktheme.Qt.QtSvg',
 'qdarktheme.Qt.QtWidgets',
 'qdarktheme.designer_supporter',
 'qdarktheme.examples',
 'qdarktheme.examples.line',
 'qdarktheme.examples.lineedit',
 'qdarktheme.examples.pushbutton',
 'qdarktheme.examples.sidebar',
 'qdarktheme.examples.widget_gallery',
 'qdarktheme.examples.widget_gallery.ui']

package_data = \
{'': ['*'],
 'qdarktheme': ['svg/*',
                'svg/dark/*',
                'svg/example/*',
                'svg/light/*',
                'theme/*']}

install_requires = \
['typing-extensions>=3.10.0,<4.0.0']

setup_kwargs = {
    'name': 'pyqtdarktheme',
    'version': '0.1.1',
    'description': 'Dark theme for PySide, PyQt and Qt Designer.',
    'long_description': 'PyQtDarkTheme\n=============\n\n[![PyPI version](https://badge.fury.io/py/pyqtdarktheme.svg)](https://badge.fury.io/py/pyqtdarktheme)\n[![License](https://img.shields.io/github/license/5yutan5/PyQtDarkTheme)](/LICENSE)\n[![Total alerts](https://img.shields.io/lgtm/alerts/g/5yutan5/PyQtDarkTheme.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/5yutan5/PyQtDarkTheme/alerts/)\n[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/5yutan5/PyQtDarkTheme.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/5yutan5/PyQtDarkTheme/context:python)\n\nDark theme for PySide, PyQt and Qt Designer.\n\nThis python module applies a theme to a Qt applications(PySide6, PyQt6, PyQt5 and PySide2) using a qt stylesheets system.  \nThere\'s a Light Theme too. Color and style balanced from the Dark theme for easy viewing in daylight.\n\n### Dark Theme\n![widget_gallery_dark_theme](https://raw.githubusercontent.com/5yutan5/PyQtDarkTheme/main/images/widget_gallery_dark.png)\n\n### Light Theme\n![widget_gallery_light_them](https://raw.githubusercontent.com/5yutan5/PyQtDarkTheme/main/images/widget_gallery_light.png)\n\n## Requirements\n\n- [Python 3.7+](https://www.python.org/downloads/release/python-396/)\n- PySide6, PyQt6, PyQt5 or PySide2\n\n## Installation\n\n```plaintext\npip install pyqtdarktheme\n```\n\nThis command requires [Git](https://git-scm.com/downloads).\n\n## Usage\n\n```Python\nimport sys\n\nimport qdarktheme\nfrom PySide6.QtWidgets import QApplication, QMainWindow, QPushButton\n\napp = QApplication(sys.argv)\nmain_win = QMainWindow()\npush_button = QPushButton("PyQtDarkTheme!!")\nmain_win.setCentralWidget(push_button)\n\napp.setStyleSheet(qdarktheme.load_stylesheet())\n\nmain_win.show()\n\napp.exec()\n\n```\n\n### Light theme\n\n```Python\napp.setStyleSheet(qdarktheme.load_stylesheet("light"))\n```\n\n### Check common widgets\n\nInput the following command in a terminal to check common widgets.\n\n```plaintext\npython -m qdarktheme.examples.widget_gallery\n```\n\n## Custom Properties\n\nThis module provides several custom properties.  \nYou can use `setProperty()` of the widget object to apply a modern style.\n\nFor example, if you set the QToolbar `type` property to `sidebar`, the style for the sidebar will be applied.\n\n```Python\nsidebar = QToolBar()\nsidebar.setProperty("type", "sidebar")\n```\n\n| Widget      | Property | Property value            | Default  | Command for demo                                                                                                                            |\n|-------------|----------|---------------------------|----------|---------------------------------------------------------------------------------------------------------------------------------------------|\n| QToolBar    | type     | toolbar, sidebar          | toolbar  | [`python -m qdarktheme.examples.sidebar`](https://github.com/5yutan5/PyQtDarkTheme/blob/main/qdarktheme/examples/sidebar/__main__.py)       |\n| QPushButton | type     | outlined, contained, text | outlined | [`python -m qdarktheme.examples.pushbutton`](https://github.com/5yutan5/PyQtDarkTheme/blob/main/qdarktheme/examples/pushbutton/__main__.py) |\n| QLineEdit   | state    | normal, warning, error    | normal   | [`python -m qdarktheme.examples.lineedit`](https://github.com/5yutan5/PyQtDarkTheme/blob/main/qdarktheme/examples/lineedit/__main__.py)     |\n| QFrame      | type     | normal, h_line, v_line    | normal   | [`python -m qdarktheme.examples.line`](https://github.com/5yutan5/PyQtDarkTheme/blob/main/qdarktheme/examples/line/__main__.py)             |\n\n## Support Qt Designer\n\nThis module support Qt Designer.\n\nHow to use PyQtDarktheme with Qt Designer.\n1. Run the following command in the terminal to launch the app that creates the template for the designer.  \n   ```plaintext\n   python -m qdarktheme.designer_supporter\n   ```\n1. Select a theme(dark or light) and press the Create button to create a template in any folder.\n1. Copy the style sheet displayed in the text box.\n1. Start Qt designer and save the ui file in the root of the template you created.\n1. Paste the copied stylesheet into the top-level widget.\n1. Register the resource file(.qrc) in the template to the resource browser.\n\n> ⚠ Support for Qt’s resource system has been removed in PyQt6. Therefore, if you want to use Qt Designer in PyQt6, you need to delete the stylesheet in the ui file and load the stylesheet using `load_stylesheet()`.\n\n## License\n\nThe icons used in the demo code are sourced from the [Material design icons](https://fonts.google.com/icons)(Apache License Version 2.0).  \nAny file not listed the [NOTICE.md](https://github.com/5yutan5/PyQtDarkTheme/blob/main/NOTICE.md) file is covered by PyQtDarkTheme\'s MIT license.',
    'author': 'Yunosuke Ohsugi',
    'author_email': '63651161+5yutan5@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/5yutan5/PyQtDarkTheme',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
