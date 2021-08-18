from setuptools import setup

with open("README.md") as file:
    read_me_description = file.read()


setup(name='cn_tcp_server',
      version='0.0',
      description='Simple server and client for chatting',
      long_description=read_me_description,
      long_description_content_type="text/markdown",
      url='https://github.com/cl1ckname/tcp_chat',
      packages=['tcp_chat'],
      classifiers=[
        "Programming Language :: Python :: 3.6",
      ],
      author_email='20002mc@gmail.com',
      zip_safe=False)  