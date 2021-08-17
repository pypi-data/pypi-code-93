# setup.py
# Copyright (C) 2020 Fracpete (fracpete at gmail dot com)

from setuptools import setup


def _read(f):
    """
    Reads in the content of the file.
    :param f: the file to read
    :type f: str
    :return: the content
    :rtype: str
    """
    return open(f, 'rb').read()


setup(
    name="python-pulseaudio-profiles-trayicon",
    description="Integrates the python-pulseaudion-profiles library into the system tray icon on Linux.",
    long_description=(
        _read('DESCRIPTION.rst') + b'\n' +
        _read('CHANGES.rst')).decode('utf-8'),
    url="https://github.com/fracpete/python-pulseaudio-profiles-trayicon",
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Topic :: Multimedia :: Sound/Audio',
        'Programming Language :: Python :: 3',
        'Operating System :: POSIX :: Linux',
    ],
    license='MIT License',
    package_dir={
        '': 'src'
    },
    packages=[
        "pypulseprofilestray",
    ],
    include_package_data=True,
    version="0.0.2",
    author='Peter "fracpete" Reutemann',
    author_email='fracpete@gmail.com',
    install_requires=[
        "python-pulseaudio-profiles>=0.0.3",
        "pycairo",
        "PyGObject",
    ],
    data_files = [
        ('share/applications/', ['share/applications/ppp-tray.desktop']),
        ('share/icons/', ['share/icons/ppp-tray.png']),
    ],
    entry_points={
        "console_scripts": [
            "ppp-tray=pypulseprofilestray.tray:sys_main",
        ]
    }
)
