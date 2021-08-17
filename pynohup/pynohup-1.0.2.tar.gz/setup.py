#-*- coding: utf-8 -*-

try:
	from  setuptools import setup

except:

	from distutils.core import setup

"""

打包的用的setup必须引入，

"""



NAME = "pynohup"

"""

名字，一般放你包的名字即可

"""

PACKAGES =["pynohup", ]

"""

包含的包，可以多个，这是一个列表

"""

DESCRIPTION ="this is a simple  logging package "

"""

关于这个包的描述

"""

LONG_DESCRIPTION = '后台运行python文件'

"""

参见read方法说明

"""

KEYWORDS ="pynohup python package""""

关于当前包的一些关键字，方便PyPI进行分类。

"""

AUTHOR ="HanyangNiu"



AUTHOR_EMAIL ="niuhanyang@163.com"



URL ="http://www.nnzhp.cn/archives/646"
"""

你这个包的项目地址，如果有，给一个吧，没有你直接填写在PyPI你这个包的地址也是可以的

"""

VERSION ="1.0.2"

"""

当前包的版本，这个按你自己需要的版本控制方式来

"""

LICENSE ="MIT"

"""

授权方式，我喜欢的是MIT的方式，你可以换成其他方式

"""

setup(

	name=
	NAME,

	version=
	VERSION,

	description=
	DESCRIPTION,

	long_description=
	LONG_DESCRIPTION,

	classifiers=
	[

		'License :: OSI Approved :: MIT License',

		'Programming Language :: Python',

		'Intended Audience :: Developers',

		'Operating System :: OS Independent',

	],

	keywords=
	KEYWORDS,

	author=
	AUTHOR,

	author_email=
	AUTHOR_EMAIL,

	url=
	URL,

	license=
	LICENSE,

	packages=
	PACKAGES,

	include_package_data=True,

	zip_safe=True,

)



## 把上面的变量填入了一个setup()中即可。
