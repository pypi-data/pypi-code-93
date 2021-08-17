# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['music_sampler', 'music_sampler.actions', 'music_sampler.app_blocks']

package_data = \
{'': ['*'], 'music_sampler': ['locales/fr/LC_MESSAGES/*']}

install_requires = \
['Kivy>=2.0.0,<3.0.0',
 'PyYAML>=5.4.1,<6.0.0',
 'pydub>=0.25.1,<0.26.0',
 'sounddevice>=0.4.2,<0.5.0',
 'transitions>=0.8.8,<0.9.0']

entry_points = \
{'console_scripts': ['music_sampler = music_sampler.app:main']}

setup_kwargs = {
    'name': 'music-sampler',
    'version': '1.6.0',
    'description': 'A music player which associates each key on the keyboard to a set of actions to run',
    'long_description': 'Music Sampler is a music player which associates each key on the keyboard to a\nset of actions to run.\n\nSee full documentation in documentation_fr.md or documentation_en.md\n\nGit repository:\nhttps://git.immae.eu/cgit/perso/Immae/Projets/Python/MusicSampler.git/about/\n\nBug Tracker:\nhttps://git.immae.eu/mantisbt/view_all_bug_page.php?project_id=1\n\nContributors:\nIsmaël Bouya\nDenise Maurice\n',
    'author': 'Ismaël Bouya',
    'author_email': 'ismael.bouya@normalesup.org',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://git.immae.eu/cgit/perso/Immae/Projets/Python/MusicSampler.git/about/',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
