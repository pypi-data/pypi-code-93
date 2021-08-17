# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['unifonter']
entry_points = \
{'console_scripts': ['unifonter = unifonter:main']}

setup_kwargs = {
    'name': 'unifonter',
    'version': '0.5.0',
    'description': 'A filter that tries to make ASCII fancy with the help of Unicode',
    'long_description': '# unifonter\nunifonter is a filter that tries to make ASCII fancy with the help of Unicode\n\n# quick intro\n\n`unifonter` is meant to be used as a filter, or as a quick lookup /\ntranslation tool. So you can use it either like\n\n    $ man man | unifonter\n    𝔐𝔄𝔑(1)                        𝔐𝔞𝔫𝔲𝔞𝔩 𝔭𝔞𝔤𝔢𝔯 𝔲𝔱𝔦𝔩𝔰                        𝔐𝔄𝔑(1)\n\n    𝔑𝔄𝔐𝔈\n           𝔪𝔞𝔫 - 𝔞𝔫 𝔦𝔫𝔱𝔢𝔯𝔣𝔞𝔠𝔢 𝔱𝔬 𝔱𝔥𝔢 𝔰𝔶𝔰𝔱𝔢𝔪 𝔯𝔢𝔣𝔢𝔯𝔢𝔫𝔠𝔢 𝔪𝔞𝔫𝔲𝔞𝔩𝔰\n\n    𝔖𝔜𝔑𝔒𝔓𝔖ℑ𝔖\n           𝔪𝔞𝔫 [𝔪𝔞𝔫 𝔬𝔭𝔱𝔦𝔬𝔫𝔰] [[𝔰𝔢𝔠𝔱𝔦𝔬𝔫] 𝔭𝔞𝔤𝔢 ...] ...\n           𝔪𝔞𝔫 -𝔨 [𝔞𝔭𝔯𝔬𝔭𝔬𝔰 𝔬𝔭𝔱𝔦𝔬𝔫𝔰] 𝔯𝔢𝔤𝔢𝔵𝔭 ...\n           𝔪𝔞𝔫 -𝔎 [𝔪𝔞𝔫 𝔬𝔭𝔱𝔦𝔬𝔫𝔰] [𝔰𝔢𝔠𝔱𝔦𝔬𝔫] 𝔱𝔢𝔯𝔪 ...\n           𝔪𝔞𝔫 -𝔣 [𝔴𝔥𝔞𝔱𝔦𝔰 𝔬𝔭𝔱𝔦𝔬𝔫𝔰] 𝔭𝔞𝔤𝔢 ...\n\nor\n\n    $ unifonter Hello\n    ℍ𝕖𝕝𝕝𝕠\n\nSeveral different styles are supported; use `-k` followed by a style\ncombination you want, otherwise one is chosen at random.\n\nSupported styles can be seen via `unifonter -d`:\n\n  Use | To get\n-----:|:-----\n  `b` | 𝐁𝐨𝐥𝐝\n  `i` | 𝐼𝑡𝑎𝑙𝑖𝑐\n `bi` | 𝑩𝒐𝒍𝒅 𝑰𝒕𝒂𝒍𝒊𝒄\n  `s` | 𝖲𝖺𝗇𝗌-𝖲𝖾𝗋𝗂𝖿\n `bs` | 𝗦𝗮𝗻𝘀-𝗦𝗲𝗿𝗶𝗳 𝗕𝗼𝗹𝗱\n `is` | 𝘚𝘢𝘯𝘴-𝘚𝘦𝘳𝘪𝘧 𝘐𝘵𝘢𝘭𝘪𝘤\n`bis` | 𝙎𝙖𝙣𝙨-𝙎𝙚𝙧𝙞𝙛 𝘽𝙤𝙡𝙙 𝙄𝙩𝙖𝙡𝙞𝙘\n  `c` | 𝒮𝒸𝓇𝒾𝓅𝓉\n `bc` | 𝓑𝓸𝓵𝓭 𝓢𝓬𝓻𝓲𝓹𝓽\n  `d` | 𝔻𝕠𝕦𝕓𝕝𝕖-𝕊𝕥𝕣𝕦𝕔𝕜\n  `f` | 𝔉𝔯𝔞𝔨𝔱𝔲𝔯\n `bf` | 𝕭𝖔𝖑𝖉 𝕱𝖗𝖆𝖐𝖙𝖚𝖗\n  `k` | Sᴍᴀʟʟ-Cᴀᴘꜱ\n  `m` | 𝙼𝚘𝚗𝚘𝚜𝚙𝚊𝚌𝚎\n  `w` | Ｆｕｌｌｗｉｄｔｈ\n\nbut note the order of the letters doesn\'t matter (`-k bis` is the same\nas `-k sib`), so if you find that you think "fraktur bold" instead of\n"bold fraktur", just go with it.\n\nSome other options are supported; see the output of `-h`.\n',
    'author': 'John R. Lenton',
    'author_email': 'jlenton@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/chipaca/unifonter',
    'py_modules': modules,
    'entry_points': entry_points,
    'python_requires': '>=3.6,<4.0',
}


setup(**setup_kwargs)
