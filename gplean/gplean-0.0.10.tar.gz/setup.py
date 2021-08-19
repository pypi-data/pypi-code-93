from setuptools import setup, find_packages


requirements = []

setup(
      name="gplean",
      version = "0.0.10", #@version@#
      description="handle,.in progressing..,APIs",
      author="3620373489",
      url="https://github.com/3620373489/gplean",
      author_email='', 
      license="MIT",
      long_description = "refer to .md files in https://github.com/3620373489/gplean",
      classifiers=[
          'Environment :: Console',
          'Environment :: Web Environment',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: Developers',
          'Intended Audience :: System Administrators',
          'Programming Language :: Python',
          ],
      packages= find_packages(),
      entry_points={
          'console_scripts': [
              'gplean_user_regis=gplean.bin.user_regis:main',
              'gplean_user_login=gplean.bin.user_login:main',
              'gplean_user_me=gplean.bin.user_me:main',
              'gplean_user_update=gplean.bin.user_update:main',
              'gplean_user_get_all_users=gplean.bin.user_get_all_users:main',
              'gplean_user_modify_password_via_xlc_sess=gplean.bin.user_modify_password_via_xlc_sess:main',
              'gplean_obj_creat_cls=gplean.bin.obj_creat_cls:main',
              'gplean_obj_del_one_row=gplean.bin.obj_del_one_row:main',
              'gplean_obj_insert_one_row=gplean.bin.obj_insert_one_row:main',
              'gplean_obj_update_one_row=gplean.bin.obj_update_one_row:main',
              'gplean_query_count=gplean.bin.query_count:main',
              'gplean_query_query=gplean.bin.query_query:main',
              'gplean_cfg_enable_regis=gplean.bin.cfg_enable_regis:main',
               
          ]
      },
      package_data={
          'resources':['RESOURCES/*']
      },
      include_package_data=True,
      install_requires=requirements,
      py_modules=['gplean'], 
)


# python3 setup.py bdist --formats=tar
# python3 setup.py sdist










