# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['sublime_music',
 'sublime_music.adapters',
 'sublime_music.adapters.filesystem',
 'sublime_music.adapters.subsonic',
 'sublime_music.dbus',
 'sublime_music.players',
 'sublime_music.ui',
 'sublime_music.ui.common']

package_data = \
{'': ['*'],
 'sublime_music.adapters': ['icons/*', 'images/*'],
 'sublime_music.adapters.subsonic': ['icons/*'],
 'sublime_music.dbus': ['mpris_specs/*'],
 'sublime_music.ui': ['icons/*', 'images/*']}

install_requires = \
['PyGObject>=3.38.0,<4.0.0',
 'bleach>=3.3.0',
 'dataclasses-json>=0.5.2,<0.6.0',
 'deepdiff>=5.0.2,<6.0.0',
 'fuzzywuzzy>=0.18.0,<0.19.0',
 'peewee>=3.13.3,<4.0.0',
 'python-Levenshtein>=0.12.0,<0.13.0',
 'python-dateutil>=2.8.1,<3.0.0',
 'python-mpv>=0.5.2,<0.6.0',
 'requests>=2.24.0,<3.0.0',
 'semver>=2.10.2,<3.0.0']

extras_require = \
{'chromecast': ['pychromecast>=9.1.1,<10.0.0'],
 'keyring': ['keyring>=23.0.0,<24.0.0'],
 'server': ['bottle>=0.12.18,<0.13.0']}

entry_points = \
{'console_scripts': ['sublime-music = sublime_music.__main__:main']}

setup_kwargs = {
    'name': 'sublime-music',
    'version': '0.11.13',
    'description': 'A native GTK *sonic client.',
    'long_description': ".. image:: https://gitlab.com/sublime-music/sublime-music/-/raw/master/logo/logo.png\n   :alt: Sublime Music Logo\n\nSublime Music is a native, GTK3\n`Subsonic`_/`Airsonic`_/`Revel`_/`Gonic`_/`Navidrome`_/`Ampache`_/\\*sonic client for the\nLinux Desktop.\n\nCI\n  .. image:: https://gitlab.com/sublime-music/sublime-music/badges/master/pipeline.svg\n     :target: https://gitlab.com/sublime-music/sublime-music/pipelines\n     :alt: GitLab build status\n  .. image:: https://builds.sr.ht/~sumner/sublime-music/commits/build.yml.svg\n     :target: https://builds.sr.ht/~sumner/sublime-music/commits/build.yml\n     :alt: sourcehut build status\n  .. image:: https://gitlab.com/sublime-music/sublime-music/badges/master/coverage.svg\n     :target: https://sublime-music.gitlab.io/sublime-music/htmlcov\n     :alt: code coverage report\n\nCommunity\n  .. image:: https://img.shields.io/matrix/sublime-music:matrix.org?logo=matrix\n     :target: https://matrix.to/#/!veTDkgvBExJGKIBYlU:matrix.org?via=matrix.org\n     :alt: Matrix chat\n  .. image:: https://img.shields.io/pypi/l/sublime-music?color=0c0\n     :target: https://gitlab.com/sublime-music/sublime-music/-/blob/master/LICENSE\n     :alt: GPLv3 or later\n  .. image:: http://img.shields.io/liberapay/receives/sumner.svg?logo=liberapay\n     :target: https://liberapay.com/sumner/donate\n     :alt: liberapay donate\n\nPackages\n  .. image:: https://repology.org/badge/vertical-allrepos/sublime-music.svg?columns=3\n     :target: https://repology.org/project/sublime-music/versions\n     :alt: Packaging status\n\n.. _Subsonic: http://www.subsonic.org/pages/index.jsp\n.. _Airsonic: https://airsonic.github.io/\n.. _Revel: https://gitlab.com/robozman/revel\n.. _Gonic: https://github.com/sentriz/gonic\n.. _Navidrome: https://www.navidrome.org/\n.. _Ampache: http://ampache.org/\n\n-------------------------------------------------------------------------------\n\n.. figure:: https://gitlab.com/sublime-music/sublime-music/-/raw/master/docs/_static/screenshots/play-queue.png\n   :align: center\n   :target: https://gitlab.com/sublime-music/sublime-music/-/raw/master/docs/_static/screenshots/play-queue.png\n\n   The Albums tab of Sublime Music with the Play Queue opened. `More\n   Screenshots <https://sublime-music.gitlab.io/sublime-music/screenshots.html>`_\n\nFeatures\n--------\n\n* Switch between multiple Subsonic-API-compliant [1]_ servers.\n* Play music through Chromecast devices on the same LAN.\n* Offline Mode where Sublime Music will not make any network requests.\n* DBus MPRIS interface integration for controlling Sublime Music via clients\n  such as ``playerctl``, ``i3status-rust``, KDE Connect, and many commonly used\n  desktop environments.\n* Browse songs by the sever-reported filesystem structure, or view them\n  organized by ID3 tags in the Albums, Artists, and Playlists views.\n* Intuitive play queue.\n* Create/delete/edit playlists.\n* Download songs for offline listening.\n\n.. [1] Requires a server which implements the Subsonic API version 1.8.0+.\n\nInstallation\n------------\n\n**Via the AUR**:\n\nInstall the |AUR Package|_. Example using ``yay``::\n\n    yay -S sublime-music\n\nIf you want support for storing passwords in the system keychain, also install\n``python-keyring``.\n\nIf you want support for playing on Chromecast devices, install\n``python-pychromecast``. If you want to serve cached files from your computer\nover the LAN to Chromecast devices also install ``python-bottle``.\n\n.. |AUR Package| replace:: ``sublime-music`` package\n.. _AUR Package: https://aur.archlinux.org/packages/sublime-music/\n\n**Via NixOS**:\n\nSublime Music is part of the ``nixos-20.09`` channel and newer (including\n``nixos-unstable``).\n\nTo install Sublime Music on NixOS, either use the declarative or the imperative\nway:\n\n- In ``configuration.nix`` (declarative)::\n\n    environment.systemPackages = [ pkgs.sublime-music ];\n\n- In command line (imperative)::\n\n    nix-env -iA sublime-music\n\nTo customize the extra components installed, you need to use the ``override``\nfunction provided by Nix::\n\n    (sublime-music.override {\n      serverSupport = true;\n      chromecastSupport = true;\n    })\n\nThe following components are supported:\n\n* ``chromecastSupport``: if you want support for playing on Chromecast devices\n  on the LAN. Defaults to ``false``.\n* ``serverSupport``: if you want to be able to serve cached files from your\n  computer over the LAN to Chromecast devices. Defaults to ``false``.\n* ``keyringSupport``: if you want to store your passwords in the system keyring\n  instead of in plain-text. Defaults to ``true``.\n* ``notifySupport``: if you want to enable notifications when a new song begins\n  to play. Defaults to ``true``.\n* ``networkSupport``: if you want to change the address used to access the\n  server depending on what network you are connected to. Defaults to ``true``.\n\nSee `Nix package management`_ for more information.\n\n.. _Nix package management: https://nixos.org/nixos/manual/index.html#sec-package-management\n\n**Via the Debian package**\n\nSublime Music is not currently in the Debian 'Stable' distribution, but has been\npackaged for Debian 'Unstable' and 'Testing'.\n\nIf you have these sources in your ``/etc/apt/sources.list``, you can install\nthe package with::\n\n    sudo apt install sublime-music\n\n**Via PyPi**::\n\n    pip install sublime-music\n\nThere are a few optional dependencies that you can install. Here's an example of\nhow to do that::\n\n    pip install sublime-music[keyring,chromecast,server]\n\n* ``keyring``: if you want to store your passwords in the system keyring instead\n  of in plain-text\n* ``chromecast``: if you want support for playing on Chromecast devices on the\n  LAN.\n* ``server``: if you want to be able to serve cached files from your computer\n  over the LAN to Chromecast devices\n\n.. note::\n\n   Sublime Music requires Python 3.8. Please make sure that you have that\n   installed. You may also need to use ``pip3`` instead of ``pip`` if you are on\n   an OS that hasn't deprecated Python 2 yet.\n\n-------------------------------------------------------------------------------\n\n|website|_\n\n.. |website| replace:: **Click HERE for the Sublime Music website.**\n.. _website: https://sublimemusic.app\n\n|userdoc|_\n\n.. |userdoc| replace:: **Click HERE for extended user documentation.**\n.. _userdoc: https://sublime-music.gitlab.io/sublime-music/\n\nSee the |contributing|_ document for how to contribute to this project.\n\n.. |contributing| replace:: ``CONTRIBUTING.md``\n.. _contributing: https://gitlab.com/sublime-music/sublime-music/-/blob/master/CONTRIBUTING.md\n\nYou can also join the conversation in our Matrix room:\n`#sublime-music:matrix.org <https://matrix.to/#/!veTDkgvBExJGKIBYlU:matrix.org?via=matrix.org>`_.\n",
    'author': 'Sumner Evans',
    'author_email': 'inquiries@sumnerevans.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://sublimemusic.app',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
