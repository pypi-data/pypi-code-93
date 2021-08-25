# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['xcodeproj']

package_data = \
{'': ['*']}

install_requires = \
['appdirs>=1.0,<2.0', 'deserialize>=1.8.0,<2.0.0']

setup_kwargs = {
    'name': 'xcodeproj',
    'version': '0.10.0',
    'description': "A utility for interacting with Xcode's xcodeproj bundle format.",
    'long_description': '# xcodeproj\n\n`xcodeproj` is a utility for interacting with Xcode\'s xcodeproj bundle format.\n\nIt expects some level of understanding of the internals of the pbxproj format and schemes. Note that this tool only reads projects. It does not write out any changes. If you are looking for more advanced functionality like this, I recommend looking at the Ruby gem of the same name (which is unaffiliated in anyway). \n\nTo learn more about the format, you can look at any of these locations:\n\n* <http://www.monobjc.net/xcode-project-file-format.html>\n* <https://www.rubydoc.info/gems/xcodeproj/Xcodeproj/Project>\n\n## Getting Started\n\nLoading a project is very simple:\n\n```python\nproject = xcodeproj.XcodeProject("/path/to/project.xcodeproj")\n```\n\nFrom here you can explore the project in different ways:\n\n```python\n\n# Get all targets\nfor target in project.targets:\n    print(target.name)\n\n# Print from the root level, 2 levels deep (.project is a property on the root \n# project as other properties such as .schemes are also available)\nfor item1 in project.project.main_group.children:\n    print(item1)\n    if not isinstance(item1, xcodeproj.PBXGroup):\n        continue\n\n    for item2 in item1.children:\n        print("\\t", item2)\n\n# Check that all files referenced in the project exist on disk\nfor item in project.fetch_type(xcodeproj.PBXFileReference).values():\n    assert os.path.exists(item.absolute_path())\n\n# You can access the raw objects map directly:\nobj = project.objects["key here"]\n\n# For any object you have, you can access its key/identifier via the \n# `.object_key` property\nkey = obj.object_key\n```\n\nNote: This library is "lazy". Many things aren\'t calculated until they are used. This time will be inconsequential on smaller projects, but on larger ones, it can save quite a bit of time due to not parsing the entire project on load. These properties are usually stored though so that subsequent accesses are instant.\n\n## Note on Scheme Support\nThere\'s no DTD for xcscheme files, so the implementation has been guessed. There will definitely be holes that still need to be patched in it though. Please open an issue if you find any, along with a sample xcscheme file.\n\n## Contributing\n\nThis project welcomes contributions and suggestions.  Most contributions require you to agree to a\nContributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us\nthe rights to use your contribution. For details, visit https://cla.opensource.microsoft.com.\n\nWhen you submit a pull request, a CLA bot will automatically determine whether you need to provide\na CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions\nprovided by the bot. You will only need to do this once across all repos using our CLA.\n\nThis project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).\nFor more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or\ncontact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.\n\n## Trademarks\n\nThis project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft \ntrademarks or logos is subject to and must follow \n[Microsoft\'s Trademark & Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks/usage/general).\nUse of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.\nAny use of third-party trademarks or logos are subject to those third-party\'s policies.\n',
    'author': 'Dale Myers',
    'author_email': 'dalemy@microsoft.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Microsoft/xcodeproj',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.7,<4.0',
}


setup(**setup_kwargs)
