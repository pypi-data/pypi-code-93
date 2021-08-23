import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pnow",  # Replace with your own username
    version="0.0.1",
    author="PredictNow.ai",
    author_email="tech@predictnow.ai",
    description="A restful client library, designed to access predictnow restful API.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/PredictNowAI/predictnow-api",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "pnow"},
    python_requires='>=3.7',
    install_requires=['aiohttp==3.7.4.post0', 'aiohttp-cors==0.7.0', 'aioredis==1.3.1', 'alembic==1.6.5', 'amqp==5.0.6', 'astunparse==1.6.3', 'async-timeout==3.0.1', 'attrs==21.2.0', 'beautifulsoup4==4.9.3', 'billiard==3.6.4.0', 'blessings==1.7', 'blinker==1.4', 'boto3==1.17.30', 'botocore==1.20.91', 'CacheControl==0.12.6', 'cachetools==4.2.2', 'category-encoders==2.2.2', 'celery==5.1.2', 'certifi==2021.5.30', 'cffi==1.14.5', 'chardet==3.0.4', 'click==7.1.2', 'click-didyoumean==0.0.3', 'click-plugins==1.1.1', 'click-repl==0.2.0', 'colorama==0.4.4', 'colorful==0.5.4', 'cryptography==3.4.7', 'cycler==0.10.0', 'dnspython==2.1.0', 'dominate==2.6.0', 'email-validator==1.1.2', 'et-xmlfile==1.1.0', 'filelock==3.0.12', 'firebase-admin==4.4.0', 'Flask==1.1.2', 'Flask-Bootstrap==3.3.7.1', 'Flask-Bootstrap4==4.0.2', 'Flask-Login==0.5.0', 'Flask-Mail==0.9.1', 'Flask-Migrate==3.0.1', 'Flask-SQLAlchemy==2.5.1', 'Flask-WTF==0.15.1', 'future==0.18.2', 'google==3.0.0', 'google-api-core==1.30.0', 'google-api-python-client==2.8.0', 'google-auth==1.30.2', 'google-auth-httplib2==0.1.0', 'google-cloud-core==1.6.0', 'google-cloud-firestore==2.1.1', 'google-cloud-storage==1.38.0', 'google-crc32c==1.1.2', 'google-resumable-media==1.3.0', 'googleapis-common-protos==1.53.0', 'gpustat==0.6.0', 'greenlet==1.1.0', 'grpcio==1.38.0', 'gunicorn==20.0.4', 'hiredis==2.0.0', 'honeycomb-beeline==2.13.1', 'httplib2==0.19.1', 'idna==2.10', 'itsdangerous==2.0.1', 'jdcal==1.4.1', 'jedi==0.17.0', 'Jinja2==2.11.2', 'jmespath==0.10.0', 'joblib==0.17.0', 'jsons==1.3.0', 'jsonschema==3.2.0', 'kiwisolver==1.3.1', 'kombu==5.1.0', 'libhoney==1.10.0', 'lightgbm==2.3.0', 'Mako==1.1.4', 'MarkupSafe==2.0.1', 'matplotlib==3.3.2', 'msgpack==1.0.2', 'multidict==5.1.0', 'numpy==1.19.2', 'nvidia-ml-py3==7.352.0', 'opencensus==0.7.13', 'opencensus-context==0.1.2', 'openpyxl==3.0.5', 'packaging==20.9', 'pandas==1.1.3', 'patsy==0.5.1', 'paypalrestsdk==1.13.1', 'Pillow==8.2.0', 'prometheus-client==0.11.0', 'proto-plus==1.18.1', 'protobuf==3.17.3', 'psutil==5.8.0', 'py-spy==0.3.7', 'pyarrow==2.0.0', 'pyasn1==0.4.8', 'pyasn1-modules==0.2.8', 'pycparser==2.20', 'pyfcm==1.4.7', 'pyflowchart==0.1.4', 'PyJWT==1.7.1', 'PyMySQL==1.0.2', 'pyOpenSSL==20.0.1', 'pyparsing==2.4.7', 'pyrsistent==0.17.3', 'python-editor==1.0.4', 'pytimeparse==1.1.8', 'pytz==2021.1', 'PyYAML==5.4.1', 'pyzmq==20.0.0', 'ray==1.0.0', 'redis==3.4.1', 'requests==2.24.0', 'rsa==4.7.2', 's3transfer==0.3.7', 'scikit-learn==0.23.2', 'scipy==1.6.3', 'shap==0.33.0', 'six==1.16.0', 'soupsieve==2.2.1', 'SQLAlchemy==1.4.17', 'statsd==3.3.0', 'statsmodels==0.12.0', 'stripe==2.55.1', 'threadpoolctl==2.1.0', 'tqdm==4.50.2', 'typing-extensions==3.10.0.0', 'typish==1.9.2', 'uritemplate==3.0.1', 'urllib3==1.25.11', 'vine==5.0.0', 'visitor==0.1.3', 'Werkzeug==1.0.1', 'wrapt==1.12.1', 'WTForms==2.3.3', 'xlrd==1.2.0', 'yarl==1.6.3']
)

# use command: pip install -e .
# to install and test it locally before you publish it

#Packaging and publish pip
#https://packaging.python.org/tutorials/packaging-projects/
#	Generating distribution archives
#		Make sure you have the latest versions of setuptools and wheel installed:
#			python -m pip install --user --upgrade setuptools wheel
#
#		Now run this command from the same directory where setup.py is located:
#			python setup.py sdist bdist_wheel
#
#	Uploading the distribution archives
#		to upload the distribution packages. You’ll need to install Twine:
#			python -m pip install --user --upgrade twine
#
#		Once installed, run Twine to upload all of the archives under dist:
#			python -m twine upload --repository testpypi dist/*
# pypi
# python -m twine upload dist/*



# to install
# pip install -i https://test.pypi.org/simple/ predictnow-api-client
# pip install predictnow-api-client
# per october 2020
# pip install --use-feature=2020-resolver predictnow-api-client
# https://stackoverflow.com/questions/60050875/pandas-installation-failed-with-error-error-no-matching-distribution-found-for