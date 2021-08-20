#!/usr/bin/env python
import subprocess
from distutils.core import setup
from distutils.extension import Extension
from distutils.command.build import build as _build


class build(_build):
    def run(self):
        subprocess.call([
            'nasm',
            '-f',
            'elf64',
            'uname.asm'
        ])
        _build.run(self)


setup(name="uname",
    version="1.0",
    description="Get Information About Current Linux Kernel With Assembly Language & C",
    author="Ferdinand Silva",
    author_email="ferdinandsilva@ferdinandsilva.com",
    url="https://github.com/six519/uname",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python',
		'Programming Language :: C',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    download_url="https://github.com/six519/uname",
    ext_modules=[
        Extension("uname",  
            sources = ["uname.c"],
            extra_objects= ["uname.o"]
        )
    ],
    cmdclass={
        'build': build
    },
    data_files=[
        ('', ['uname.asm'])
    ]
)