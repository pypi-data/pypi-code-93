from setuptools import setup, find_packages
from os import path


setup(name='baekjoon', # 패키지 명

version='1.0.8',

description='unofficial boj api',

author='smartwe',

author_email='sparklingwee@naver.com',

url='https://github.com/smartwe/baekjoon-api',

license='MIT', # MIT에서 정한 표준 라이센스 따른다

py_modules=[''], # 패키지에 포함되는 모듈

python_requires='>=3',

install_requires=['bs4'], # 패키지 사용을 위해 필요한 추가 설치 패키지

packages=['baekjoon'], # 패키지가 들어있는 폴더들

)