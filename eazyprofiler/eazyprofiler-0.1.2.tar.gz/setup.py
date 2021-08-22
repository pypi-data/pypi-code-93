from setuptools import setup
import versioneer

requirements = [
    # package requirements go here
]

setup(
    name='eazyprofiler',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="EazyProfiler is forked version of Lazyprofiler which is a simple utility to collect CPU, GPU, RAM and GPU Memorystats while the program is running.",
    license="MIT",
    author="Damianos Park",
    author_email='damianospark@gmail.com',
    url='https://github.com/damianospark/eazyprofiler',
    packages=['eazyprofiler'],
    entry_points={
        'console_scripts': [
            'eazyprofiler=eazyprofiler.cli:cli'
        ]
    },
    install_requires=requirements,
    keywords='eazyprofiler',
    classifiers=[
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ]
)
