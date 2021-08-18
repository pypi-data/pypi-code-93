#!/usr/bin/env python

import os
import re
import sys

from setuptools import find_packages, setup

# marker for basic and basic libs in requirements.txt
BASIC_LIB_MARKER = '#basic-lib'

# libs that require Python 3.x
PYTHON3_LIBS = ['hbmqtt', 'graphql-core', 'websockets']

install_requires = []
dependency_links = []
extra_requires = []

# root code folder
THIS_FOLDER = os.path.realpath(os.path.dirname(__file__))


# determine version
with open(os.path.join(THIS_FOLDER, 'localstack_ext', 'constants.py')) as f:
    configs = f.read()
version = re.search(r'^\s*VERSION\s*=\s*[\'"](.+)[\'"]\s*$', configs, re.MULTILINE).group(1)

# read requirements
with open(os.path.join(THIS_FOLDER, 'requirements.txt')) as f:
    requirements = f.read()

for line in re.split('\n', requirements):
    if line and line[0] == '#' and '#egg=' in line:
        line = re.search(r'#\s*(.*)', line).group(1)
    if line and line[0] != '#':
        if '://' not in line:
            lib_stripped = line.split(' #')[0].strip()
            if BASIC_LIB_MARKER in line:
                install_requires.append(lib_stripped)
            else:
                extra_requires.append(lib_stripped)

if sys.version_info[:2] < (3, 4):
    # remove libs that require Python 3+
    def requires_p3(lib):
        return any([p3l in lib for p3l in PYTHON3_LIBS])
    install_requires = [d for d in install_requires if not requires_p3(d)]
    extra_requires = [d for d in extra_requires if not requires_p3(d)]


package_data = {
    '': ['*.md'],
    'localstack_ext': [
        'utils/*.py.enc',
        'utils/aws/*.py.enc',
        'services/*.py.enc',
        'services/amplify/*.py.enc',
        'services/apigateway/*.py.enc',
        'services/applicationautoscaling/*.py.enc',
        'services/appsync/*.py.enc',
        'services/athena/*.py.enc',
        'services/autoscaling/*.py.enc',
        'services/awslambda/*.py.enc',
        'services/azure/*.py.enc',
        'services/backup/*.py.enc',
        'services/batch/*.py.enc',
        'services/cloudformation/*.py.enc',
        'services/cloudfront/*.py.enc',
        'services/cloudtrail/*.py.enc',
        'services/codecommit/*.py.enc',
        'services/cognito/*.json',
        'services/cognito/*.py.enc',
        'services/costexplorer/*.py.enc',
        'services/docdb/*.py.enc',
        'services/dynamodb/*.py.enc',
        'services/ec2/*.py.enc',
        'services/ecr/*.py.enc',
        'services/ecs/*.py.enc',
        'services/efs/*.py.enc',
        'services/eks/*.py.enc',
        'services/elb/*.py.enc',
        'services/emr/*.py.enc',
        'services/elasticache/*.py.enc',
        'services/elasticbeanstalk/*.py.enc',
        'services/events/*.py.enc',
        'services/glacier/*.py.enc',
        'services/glue/*.py.enc',
        'services/iam/*.json',
        'services/iam/*.py.enc',
        'services/iot/*.py.enc',
        'services/kafka/*.py.enc',
        'services/kinesisanalytics/*.py.enc',
        'services/lakeformation/*.py.enc',
        'services/mediastore/*.py.enc',
        'services/neptune/*.py.enc',
        'services/organizations/*.py.enc',
        'services/qldb/*.py.enc',
        'services/rds/*.py.enc',
        'services/redshift/*.py.enc',
        'services/route53/*.py.enc',
        'services/s3/*.py.enc',
        'services/sagemaker/*.py.enc',
        'services/secretsmanager/*.py.enc',
        'services/serverlessrepo/*.yml',
        'services/serverlessrepo/*.py.enc',
        'services/servicediscovery/*.py.enc',
        'services/ses/*.py.enc',
        'services/sns/*.py.enc',
        'services/sqs/*.py.enc',
        'services/stepfunctions/*.py.enc',
        'services/sts/*.py.enc',
        'services/timestream/*.py.enc',
        'services/transfer/*.py.enc',
        'services/xray/*.py.enc'
    ]}


if __name__ == '__main__':

    setup(
        name='localstack-ext',
        version=version,
        description='Extensions for LocalStack',
        author='Waldemar Hummer',
        author_email='waldemar.hummer@gmail.com',
        url='https://github.com/localstack/localstack',
        packages=find_packages(exclude=('tests', 'tests.*')),
        package_data=package_data,
        install_requires=install_requires,
        dependency_links=dependency_links,
        extras_require={
            'full': extra_requires
        },
        test_suite='tests',
        zip_safe=False,
        classifiers=[
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'License :: OSI Approved :: Apache Software License',
            'Topic :: Software Development :: Testing',
        ]
    )
