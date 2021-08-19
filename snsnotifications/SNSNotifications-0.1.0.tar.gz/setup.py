import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as fh:
    requirements = fh.readlines()
    requirements = map(lambda x: x.strip(), requirements)
    requirements = filter(lambda x: len(x) > 0, requirements)
    requirements = list(requirements)

print(requirements)

setuptools.setup(name="SNSNotifications",
                 version="0.1.0",
                 author="TrinhQuan",
                 author_email="quantv@aimesoft.com",
                 description="This module use for abstract work to send notification a cross sns provider",
                 long_description=long_description,
                 url='https://gitlab.com/aimesoft/libraries/snsnotifications.git',
                 download_url='https://gitlab.com/aimesoft/libraries/snsnotifications/-/archive/master/snsnotifications-master.zip',
                 install_requires=requirements,
                 long_description_content_type="text/plain",
                 packages=setuptools.find_packages(),
                 data_files=['requirements.txt'],
                 classifiers=["Programming Language :: Python :: 3.6", "Programming Language :: Python :: 3.7",
                              "License :: OSI Approved :: MIT License"], )
