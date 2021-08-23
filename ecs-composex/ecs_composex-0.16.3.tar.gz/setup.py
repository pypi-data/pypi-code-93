# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['ecs_composex',
 'ecs_composex.acm',
 'ecs_composex.alarms',
 'ecs_composex.appmesh',
 'ecs_composex.codeguru_profiler',
 'ecs_composex.cognito_userpool',
 'ecs_composex.common',
 'ecs_composex.compute',
 'ecs_composex.dashboards',
 'ecs_composex.dns',
 'ecs_composex.docdb',
 'ecs_composex.dynamodb',
 'ecs_composex.ecr',
 'ecs_composex.ecs',
 'ecs_composex.efs',
 'ecs_composex.elasticache',
 'ecs_composex.elbv2',
 'ecs_composex.events',
 'ecs_composex.iam',
 'ecs_composex.kafka',
 'ecs_composex.kinesis',
 'ecs_composex.kms',
 'ecs_composex.rds',
 'ecs_composex.s3',
 'ecs_composex.secrets',
 'ecs_composex.sns',
 'ecs_composex.sqs',
 'ecs_composex.ssm_parameter',
 'ecs_composex.utils',
 'ecs_composex.vpc']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=5.4.1,<6.0.0',
 'aws-sam-translator>=1.38.0,<2.0.0',
 'boto3>=1.18,<2.0',
 'compose-x-common>=0.1.1,<0.2.0',
 'compose-x-render>=0.2.1,<0.3.0',
 'docker>=5.0.0,<6.0.0',
 'ecs-composex-specs>=0.2.10,<0.3.0',
 'importlib-resources>=5.2.2,<6.0.0',
 'jsonschema>=3.2.0,<4.0.0',
 'requests>=2.26.0,<3.0.0',
 'tabulate>=0.8.9,<0.9.0',
 'troposphere>=3.0,<4.0',
 'urllib3>=1.26.6,<2.0.0']

extras_require = \
{'ecrscan': ['ecr-scan-reporter>=0.3,<0.4']}

entry_points = \
{'console_scripts': ['compose-x = ecs_composex.cli:main',
                     'ecs-compose-x = ecs_composex.cli:main',
                     'ecs_compose_x = ecs_composex.cli:main']}

setup_kwargs = {
    'name': 'ecs-composex',
    'version': '0.16.3',
    'description': 'Manage, Configure and Deploy your services and AWS services and applications from your docker-compose definition',
    'long_description': '.. meta::\n    :description: ECS Compose-X\n    :keywords: AWS, ECS, Fargate, Docker, Containers, Compose, docker-compose\n\n============\nECS ComposeX\n============\n\n|PYPI_VERSION| |PYPI_LICENSE| |PY_DLS|\n\n|CODE_STYLE| |TDD| |BDD|\n\n|QUALITY|\n\n|BUILD|\n\n---------------------------------------------------------------------------------------------------------------\nManage, Configure and deploy your applications/services and AWS resources from your docker-compose definitions\n---------------------------------------------------------------------------------------------------------------\n\nUseful Links\n===============\n\n* `Documentation`_\n* `Blog`_\n* `Labs <https://labs.compose-x.io/>`_\n* `Feature requests <https://github.com/compose-x/ecs_composex/projects/2>`_\n* `Issues <https://github.com/compose-x/ecs_composex/projects/3>`_\n* `Compatibility Matrix`_\n\n\nWhy use ECS Compose-X?\n========================\n\nAs a developer, working locally is a crucial part of your day to day work, and **docker-compose** allows you to do\njust that, for simple services as well as very complex structures.\n\nYour prototype works, and you want to deploy to AWS. But what about IAM ? Networking ? Security ? Configuration ?\n\nUsing ECS Compose-X, you keep your docker-compose definitions as they are, add the AWS services you have chosen\nas part of that definition, such as ELB, RDS/DynamodDB Databases etc, and the program will automatically\ngenerate all the AWS CloudFormation templates required to deploy all your services.\n\nIt automatically takes care of network access requirements and IAM permissions, following best practices.\n\n\nInstallation\n============\n\nECS Compose-X can be used as a CLI ran locally, in CICD pipelines, or as an AWS CloudFormation macro, allowing you\nto use your Docker Compose files directly in CloudFormation!\n\nOn AWS using AWS CloudFormation Macro\n--------------------------------------\n\nYou can now deploy the CloudFormation macro to your AWS Account using AWS Serverless Application Repository (SAR).\n\nDeploy it in your account today |AWS_SAR|\n\n.. |AWS_SAR| image:: https://s3.amazonaws.com/cloudformation-examples/cloudformation-launch-stack.png\n    :target: https://serverlessrepo.aws.amazon.com/applications/eu-west-1/518078317392/compose-x\n\n\n`Find out how to use ECS Compose-X in AWS here`_\n\nVia pip\n--------\n\n.. code-block:: bash\n\n    pip install ecs_composex\n\n\nHow is it different ?\n=====================\n\nThere are a lot of similar tools out there, including published by AWS. So here are a few of the features\nthat we think could be of interest to you.\n\nModularity / "Plug & Play"\n---------------------------\n\nThe majority of people who are going to use ECS ComposeX on a daily basis should be developers who need to have an\nenvironment of their own and want to quickly iterate over it.\n\nHowever, it is certainly something that Cloud Engineers in charge of the AWS accounts etc. would want to use to make their own lives easy too.\n\nIn many areas, you as the end-user of ComposeX will already have infrastructure in place: VPC, DBs and what not.\nSo as much as possible, you will be able in ComposeX to define `Lookup`_ sections which will find your existing resources,\nand map these to the services.\n\nBuilt for AWS Fargate\n----------------------\n\nHowever the original deployments and work on this project was done using EC2 instances (using SpotFleet), everything\nis now implemented to work on AWS Fargate First (2020-06-06).\n\nThat said, all features that can be supported with EC2 instances are available to you with ECS Compose-X, which, will\nsimply disable such settings when deployed on top of AWS Fargate.\n\nAttributes auto-correct\n-------------------------\n\nA fair amount of the time, deployments via AWS CloudFormation, Ansible and other IaC will fail because of incompatible\nsettings. This happened a number of times, with a lot of different AWS Services.\n\nWhilst giving you the ability to use all properties of AWS CloudFormation objects, whenever possible, ECS Compose-X\nwill understand how two services are connected and will auto-correct the settings for you.\n\nFor example, if you set the Log retention to be 42 days, which is invalid, it will automatically change that to the\nclosest valid value (here, 30).\n\n\n\nCredits\n=======\n\nThis package would not have been possible without the amazing job done by the AWS CloudFormation team!\nThis package would not have been possible without the amazing community around `Troposphere`_!\n\n.. _`Mark Peek`: https://github.com/markpeek\n.. _`AWS ECS CLI`: https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ECS_CLI.html\n.. _Troposphere: https://github.com/cloudtools/troposphere\n.. _Blog: https://blog.compose-x.io/\n.. _Docker Compose: https://docs.docker.com/compose/\n.. _ECS ComposeX: https://docs.compose-x.io\n.. _YAML Specifications: https://yaml.org/spec/\n.. _Extensions fields:  https://docs.docker.com/compose/compose-file/#extension-fields\n.. _ECS ComposeX Project: https://github.com/orgs/lambda-my-aws/projects/3\n.. _CICD Pipeline for multiple services on AWS ECS with ECS ComposeX: https://blog.compose-x.io/posts/cicd-pipeline-for-multiple-services-on-aws-ecs-with-ecs-composex/\n\n.. _AWS ECS:            https://nightly.docs.compose-x.io/syntax/composex/ecs.html\n.. _AWS VPC:            https://nightly.docs.compose-x.io/syntax/composex/vpc.html\n.. _AWS RDS:            https://nightly.docs.compose-x.io/syntax/composex/rds.html\n.. _AWS DynamoDB:       https://nightly.docs.compose-x.io/syntax/composex/dynamodb.html\n.. _AWS DocumentDB:     https://nightly.docs.compose-x.io/syntax/composex/docdb.html\n.. _AWS ACM:            https://nightly.docs.compose-x.io/syntax/composex/acm.html\n.. _AWS ELBv2:          https://nightly.docs.compose-x.io/syntax/composex/elbv2.html\n.. _AWS S3:             https://nightly.docs.compose-x.io/syntax/composex/s3.html\n.. _AWS IAM:            https://nightly.docs.compose-x.io/syntax/composex/ecs.details/iam.html\n.. _AWS Kinesis:        https://nightly.docs.compose-x.io/syntax/composex/kinesis.html\n.. _AWS SQS:            https://nightly.docs.compose-x.io/syntax/composex/sqs.html\n.. _AWS SNS:            https://nightly.docs.compose-x.io/syntax/composex/sns.html\n.. _AWS KMS:            https://nightly.docs.compose-x.io/syntax/composex/kms.html\n.. _AWS ElastiCache:    https://nightly.docs.compose-x.io/syntax/composex/elasticache.html\n.. _AWS EC2:            https://nightly.docs.compose-x.io/features.html#ec2-resources-for-ecs-cluster\n.. _AWS AppMesh:        https://nightly.docs.compose-x.io/readme/appmesh.html\n.. _AWS CloudWatch:     https://nightly.docs.compose-x.io/syntax/compose_x/alarms.html\n.. _Lookup:             https://nightly.docs.compose-x.io/syntax/compose_x/common.html#lookup\n.. _the compatibilty matrix: https://nightly.docs.compose-x.io/compatibility/docker_compose.html\n.. _Compatibility Matrix: https://nightly.docs.compose-x.io/compatibility/docker_compose.html\n.. _Find out how to use ECS Compose-X in AWS here: https://blog.compose-x.io/posts/use-your-docker-compose-files-as-a-cloudformation-template/index.html\n.. _Documentation: https://docs.compose-x.io\n\n.. |BUILD| image:: https://codebuild.eu-west-1.amazonaws.com/badges?uuid=eyJlbmNyeXB0ZWREYXRhIjoiWjIrbSsvdC9jZzVDZ3N5dVNiMlJCOUZ4M0FQNFZQeXRtVmtQbWIybUZ1ZmV4NVJEdG9yZURXMk5SVVFYUjEwYXpxUWV1Y0ZaOEcwWS80M0pBSkVYQjg0PSIsIml2UGFyYW1ldGVyU3BlYyI6Ik1rT0NaR05yZHpTMklCT0MiLCJtYXRlcmlhbFNldFNlcmlhbCI6MX0%3D&branch=main\n\n.. |PYPI_VERSION| image:: https://img.shields.io/pypi/v/ecs_composex.svg\n        :target: https://pypi.python.org/pypi/ecs_composex\n\n.. |PYPI_DL| image:: https://img.shields.io/pypi/dm/ecs_composex\n    :alt: PyPI - Downloads\n    :target: https://pypi.python.org/pypi/ecs_composex\n\n.. |PYPI_LICENSE| image:: https://img.shields.io/pypi/l/ecs_composex\n    :alt: PyPI - License\n    :target: https://github.com/compose-x/ecs_composex/blob/master/LICENSE\n\n.. |PYPI_PYVERS| image:: https://img.shields.io/pypi/pyversions/ecs_composex\n    :alt: PyPI - Python Version\n    :target: https://pypi.python.org/pypi/ecs_composex\n\n.. |PYPI_WHEEL| image:: https://img.shields.io/pypi/wheel/ecs_composex\n    :alt: PyPI - Wheel\n    :target: https://pypi.python.org/pypi/ecs_composex\n\n.. |CODE_STYLE| image:: https://img.shields.io/badge/codestyle-black-black\n    :alt: CodeStyle\n    :target: https://pypi.org/project/black/\n\n.. |TDD| image:: https://img.shields.io/badge/tdd-pytest-black\n    :alt: TDD with pytest\n    :target: https://docs.pytest.org/en/latest/contents.html\n\n.. |BDD| image:: https://img.shields.io/badge/bdd-behave-black\n    :alt: BDD with Behave\n    :target: https://behave.readthedocs.io/en/latest/\n\n.. |QUALITY| image:: https://sonarcloud.io/api/project_badges/measure?project=compose-x_ecs_composex&metric=alert_status\n    :alt: Code scan with SonarCloud\n    :target: https://sonarcloud.io/dashboard?id=compose-x_ecs_composex\n\n.. |PY_DLS| image:: https://img.shields.io/pypi/dm/ecs-composex\n    :target: https://pypi.org/project/ecs-composex/\n',
    'author': 'John Preston',
    'author_email': 'john@compose-x.io',
    'maintainer': 'John Preston',
    'maintainer_email': 'john@compose-x.io',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
