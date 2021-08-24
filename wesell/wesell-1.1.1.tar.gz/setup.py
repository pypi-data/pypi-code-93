from setuptools import setup

setup(
    name='wesell',
    version="1.1.1",
    url='https://gitee.com/idollo/wesell.pylib.git',
    license='MIT',
    author='idollo',
    author_email='stone58@qq.com',
    description='wesell flask python libs.',
    long_description=__doc__,
    packages=['wesell', 'wesell.flask', 'wesell.sqlalchemy'],
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=[
        'future>=0.17.1',
        'Flask==0.12.2',
        'SQLAlchemy==1.2.9',
        'Flask-Script>=2.0.5',
        'Flask==0.12.2',
        'Flask-Celery==2.4.3',
        'Flask-HTTPAuth==3.2.3',
        'Flask-Redis==0.3.0',
        'Flask-RQ==0.2',
        'Flask-Session==0.3.1',
        'Flask-SQLAlchemy==2.1',
        'pymysql==0.9.3',
        'mysql>=0.0.2',
        'mysqlclient>=1.3.0,<1.4'
        'redis>=2.10.5',
        'celery==4.3.0',
        'hiredis==1.0.0',
        'msgpack>=0.6.2',
        'xloger>=1.6.5',
        'simplejson>=3.11.1',
        'dill>=0.3.3'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5'
    ]
)
