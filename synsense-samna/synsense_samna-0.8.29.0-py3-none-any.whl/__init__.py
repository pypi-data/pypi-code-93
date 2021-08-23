import subprocess
import sys

__gilab_packages_index_url__ = 'https://gitlab.com/api/v4/projects/27423070/packages/pypi/simple'
__version__ = '0.8.29.0'

def __upgrade__(index_url, version):
    subprocess.check_call([sys.executable, "-m", "pip", "install", 'samna==%s' % version, '--upgrade', '--index-url=%s' % index_url])

def upgrade():
    __upgrade__(__gilab_packages_index_url__, __version__)

upgrade()
