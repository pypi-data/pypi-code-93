# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['cinegraph']

package_data = \
{'': ['*']}

install_requires = \
['fire>=0.4.0,<0.5.0', 'opencv-python>=4.5.3,<5.0.0', 'tqdm>=4.62.1,<5.0.0']

entry_points = \
{'console_scripts': ['cinegraph = cinegraph.cli:execute']}

setup_kwargs = {
    'name': 'cinegraph',
    'version': '0.1.1',
    'description': 'A CLI tool that creates a kaleidescope-esque gradient image of your favorite movie.',
    'long_description': '<p align="center">\n        <img width=200px height=200px src="./docs/logo.png" alt="Cinegraph Logo"\n</p>\n\n<div align="center">\n    <a href="https://github.com/AndresMWeber/Cinegraph">\n        <img alt="Status" src="https://img.shields.io/badge/status-active-success.svg" />\n    </a>\n    <a href="https://github.com/AndresMWeber/Cinegraph/issues">\n        <img alt="Issues" src="https://img.shields.io/github/issues/andresmweber/Cinegraph.svg" />\n    </a>\n    <a href="https://github.com/AndresMWeber/Cinegraph/blob/master/LICENSE">\n        <img alt="License" src="https://img.shields.io/badge/License-BSD%203--Clause-blue.svg" />\n    </a>\n    <br />\n    <a href=".">\n        <img alt="GitHub code size in bytes" src="https://img.shields.io/github/languages/code-size/andresmweber/Cinegraph" />\n    </a>\n</div>\n<br>\n\n<p align="center"> A CLI tool that creates a kaleidescope-esque gradient image of your favorite movie.\n    <br> \n</p>\n\n<h3 align="center">\n    <code>\n    ·\n    <a href="#installation">Installation</a>\n    ·\n    </code>\n</h3>\n\n## 📝 Table of Contents\n\n- [📝 Table of Contents](#-table-of-contents)\n- [🧐 About <a name = "about"></a>](#-about-)\n- [🖥️ Screenshots <a name = "screenshots"></a>](#️-screenshots-)\n- [💨 Quickstart <a name = "quickstart"></a>](#-quickstart-)\n  - [Flags](#flags)\n- [💾 Installation](#-installation)\n  - [Prerequsites](#prerequsites)\n  - [Install steps](#install-steps)\n- [⛏️ Tech Stack <a name = "tech"></a>](#️-tech-stack-)\n- [✍️ Authors <a name = "authors"></a>](#️-authors-)\n- [🎉 Acknowledgements <a name = "acknowledgement"></a>](#-acknowledgements-)\n\n\n## 🧐 About <a name = "about"></a>\n\nA CLI tool that creates a kaleidescope-esque gradient image of your favorite movie.\n\n## 🖥️ Screenshots <a name = "screenshots"></a>\n\n<div align=center>\n<h2>Total Recall</h2>\n<img src="./examples/(2012)%20Total%20Recall_c600_b5_r1920x1080_f1_fm50.jpg" />\n\n<h2>Elysium</h2>\n<img src="./examples/(2013)%20Elysium_c600_b5_r1920x1080_f1_fm50.jpg" />\n\n<h2>Pacific Rim</h2>\n<img src="./examples/(2013)%20Pacific%20Rim_c600_b5_r1920x1080_f1_fm50.jpg" />\n\n<h2>Star Trek Into Darkness</h2>\n<img src="./examples/(2013)%20Star%20Trek%20Into%20Darkness_c600_b5_r1920x1080_f1_fm50.jpg" />\n\n<h2>Edge of Tomorrow</h2>\n<img src="./examples/Edge_of_Tomorrow_c600_b5_r1920x1080_f1_fm50.jpg" />\n\n<h2>Example Write Frames</h2>\n<img src="./examples/Elysium/f_1052.jpg" />\n<img src="./examples/Elysium/f_2367.jpg" />\n<img src="./examples/Elysium/f_108619.jpg" />\n<img src="./examples/Elysium/f_122821.jpg" />\n<img src="./examples/Elysium/f_150699.jpg" />\n<img src="./examples/Elysium/f_157274.jpg" />\n</div>\n\n## 💨 Quickstart <a name = "quickstart"></a>\nThe current run script can be invoked using:\n``` bash\n$ poetry run exec \n```\n\nIf you do not provide any positional arguments to specify input files it will automatically open a [Tkinter](https://docs.python.org/3/library/tkinter.html) file picker, you need to have a capable display window provider (if using WSL [Xserver](https://www.x.org/releases/X11R7.7/doc/man/man1/Xserver.1.xhtml) is a great option.)\n\nAdditionally you can run it with the following flags:\n### Flags\n```\nNAME\n    poetry run exec\n    cinegraph\n\nSYNOPSIS\n    poetry run exec <flags> [FILES]...\n    cinegraph <flags> [FILES]...\nPOSITIONAL ARGUMENTS\n    FILES\n        The files that you want to be processed.\n\nFLAGS\n    -c,--colors=COLORS\n        Number of colors in the Cinegraph\n        Example Input:\n            100\n    -b,--blur=BLUR\n        Blur amount for the Cinegraph\n        Example Input:\n            5\n    -r,--resolution=RESOLUTION\n        Resolution for the Cinegraph\n        Example Input:\n            1000,1200\n    -n,--no_frame=NO_FRAME\n        Remove the white border + frame for the Cinegraph\n    -m,--margin=MARGIN\n        Set the margin (in pixels) for the border around the Cinegraph\n        e.g. 25\n    -w,--write_frames=WRITE_FRAMES\n        Output the frames with a center square that denotes the dominant color.\n```\n\n## 💾 Installation\n\n### Prerequsites\n\n1. [Python](https://www.python.org/) and [Python Poetry](https://python-poetry.org/) is installed\n\n### Install steps\n1. `poetry install` (To install in the top level directory always: `poetry config virtualenvs.in-project true`)\n\n\n## ⛏️ Tech Stack <a name = "tech"></a>\n\n- [Python](https://www.python.org/) - Software Development\n- [OpenCV](https://opencv.org/) - Image Processing\n- [Fire](https://github.com/google/python-fire) - CLI Framework\n\n## ✍️ Authors <a name = "authors"></a>\n\n<a href="https://github.com/andresmweber/">\n    <img title="Andres Weber" src="https://github.com/andresmweber.png" height="50px">\n</a>\n\n## 🎉 Acknowledgements <a name = "acknowledgement"></a>\n\n- [@FFMPEG](https://www.ffmpeg.org/) for providing amazing open source video solutions.\n- [The Colors of Motion](https://thecolorsofmotion.com/) for being the inspiriation and the idea that I tried my best to mimic. \n',
    'author': 'Andres Weber',
    'author_email': 'andresmweber@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
