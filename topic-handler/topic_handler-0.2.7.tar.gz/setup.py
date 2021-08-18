from distutils.core import setup
import setuptools


setup(
    name='topic_handler',
    version='0.2.7',
    include_package_data=True,
    description='Library to  management kafka topics with faust',
    author='Andres Gonzalez',
    author_email='andres@4coders.co',
    license="GPLv3",
    # use the URL to the github repo
    url='https://github.com/4CodersColombia/event-broker-topic-handler',
    download_url='https://github.com/4CodersColombia/event-broker-topic-handler/archive/refs/tags/0.2.7.tar.gz',
    keywords=['kafka', 'faust'],
    classifiers=['Programming Language :: Python :: 3.9', ],
    packages=setuptools.find_packages(),
    install_requires=[
        'kafka-python==1.4.6',
        'betterproto==1.2.5',
        'PyJWT==1.7.1',
        'cryptography==3.4.7',
    ],
)

