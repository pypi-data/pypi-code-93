from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

def _requires_from_file(filename):
    return open(filename).read().splitlines()

# long_description(後述)に、GitHub用のREADME.mdを指定
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='fepr-py-rpa', # パッケージ名(プロジェクト名)
    packages=find_packages(), # パッケージ内(プロジェクト内)のパッケージ名をリスト形式で指定

    version='1.0.7', # バージョン

    license='MIT', # ライセンス

    install_requires=_requires_from_file('requirements.txt'),

    author='FUMiYA EMPiRE', # パッケージ作者の名前
    author_email='kamijumper336@gmail.com', # パッケージ作者の連絡先メールアドレス

    url='https://github.com/FUMiYAEMPiRE/Python_RPA_Module', # パッケージに関連するサイトのURL(GitHubなど)

    description='Sheets_api_v4, pydriveの扱いを簡易的に行うパッケージ', # パッケージの簡単な説明
    long_description=long_description, # PyPIに'Project description'として表示されるパッケージの説明文
    long_description_content_type='text/markdown', # long_descriptionの形式を'text/plain', 'text/x-rst', 'text/markdown'のいずれかから指定

    classifiers=[
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'License :: OSI Approved :: MIT License',
    ], # パッケージ(プロジェクト)の分類。https://pypi.org/classifiers/に掲載されているものを指定可能。
)