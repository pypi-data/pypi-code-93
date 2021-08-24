# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['django_fsm_freeze']

package_data = \
{'': ['*']}

install_requires = \
['Django', 'django-dirtyfields>=1.7.0,<2.0.0', 'django-fsm']

setup_kwargs = {
    'name': 'django-fsm-freeze',
    'version': '0.1.9',
    'description': 'django-fsm data immutability support',
    'long_description': "# django fsm data immutability support\n![CI](https://github.com/ming-tung/django-fsm-freeze/actions/workflows/continues-integration.yml/badge.svg?branch=main)\n[![PyPI version](https://badge.fury.io/py/django-fsm-freeze.svg)](https://badge.fury.io/py/django-fsm-freeze)\n[![Downloads](https://static.pepy.tech/personalized-badge/django-fsm-freeze?period=total&units=international_system&left_color=grey&right_color=yellowgreen&left_text=Downloads)](https://pepy.tech/project/django-fsm-freeze)\n\ndjango-fsm-freeze provides a django model mixin for data immutability based on\n[django-fsm](https://github.com/viewflow/django-fsm).\n\n\n## Installation\n\n```commandline\npip install django-fsm-freeze\n```\n\n## Configuration\n\n### Basic configuration\n- Add `FreezableFSMModelMixin` to your [django-fsm](https://github.com/viewflow/django-fsm) model\n- Specify the `FROZEN_IN_STATES` in which the object should be frozen, meaning the\n  value of its fields/attributes cannot be changed.\n- (optional) Customize the `NON_FROZEN_FIELDS` for partial mutability\n\nWhen an object is in a frozen state, by default all of its fields are immutable,\nexcept for the `state` FSMField which needs to be mutable for\n[django-fsm](https://github.com/viewflow/django-fsm) to work.\n\n```python\nfrom django_fsm import FSMField\n\nfrom django_fsm_freeze.models import FreezableFSMModelMixin\n\nclass MyDjangoFSMModel(FreezableFSMModelMixin):\n\n    # In this example, when object is in the 'active' state, it is immutable.\n    FROZEN_IN_STATES = ('active', )\n    \n    # django-fsm specifics: state, transitions, etc.\n    state = FSMField(default='new')\n    # ...\n```\n\n### Customization\n\n#### Tell django-fsm-freeze which field to look up for frozeness\nBy default, FreezableFSMModelMixin will look for the FSMField on your model\nand its value to determine whether the instance is frozen or not.\nHowever, in case your model has multiple `FSMField`s,\nyou would need to tell the Mixin which field should be used to look up,\nto determine the frozeness via the `FROZEN_STATE_LOOKUP_FIELD` attribute.\n\n```python\nfrom django.db import models\nfrom django_fsm import FSMField\n\nfrom django_fsm_freeze.models import FreezableFSMModelMixin\n\nclass MyDjangoFSMModel(FreezableFSMModelMixin):\n\n    # In this example, when object is in the 'active' state, it is immutable.\n    FROZEN_IN_STATES = ('active', )\n\n    # Assign this with the name of the `FSMField` if your models has multiple FSMFields.\n    # See example in `mytest/models.py:FakeModel2`\n    FROZEN_STATE_LOOKUP_FIELD = 'state'\n    \n    # django-fsm specifics: state, transitions, etc.\n    state = FSMField(default='new')\n    another_state = FSMField(default='draft')\n    # ...\n```\n\nIn another case, when the desired lookup state is on another model related\nvia foreign key, instead of setting `FROZEN_STATE_LOOKUP_FIELD`,\nit is possible to specify the (dot-separated) path to that field in\n`FROZEN_DELEGATE_TO`.\nThis setting instructs the freezable model instance to evaluate the freezable\nstate from that remote field.\n\n```python\nclass Parent(FreezableFSMModelMixin):\n    state = FSMField(default='new')\n\n\nclass Child(FreezableFSMModelMixin):\n\n    # Assign this with the path (dotted separated) to the instance you expect\n    # the decision for freezability to be decided on.\n    FROZEN_DELEGATE_TO = 'parent'\n    parent = models.ForeignKey(Parent, on_delete=models.PROTECT)\n```\n\n#### Define for partial mutability \nIn case we want to mutate certain fields when the object is frozen, we can\nset the `NON_FROZEN_FIELDS` to allow it.\n\n```python\nclass MyDjangoFSMModel(FreezableFSMModelMixin):\n\n    # In this example, when object is in the 'active' state, it is immutable.\n    FROZEN_IN_STATES = ('active', )\n    NON_FROZEN_FIELDS = ('a_mutable_field', )\n\n    # This field is mutable even when the object is in the frozen state.\n    a_mutable_field = models.BooleanField()\n```\nSee configuration example in https://github.com/ming-tung/django-fsm-freeze/blob/main/mytest/models.py\n\n## Usage\n\nThe frozen check takes place when\n - class is prepared (configuration checking)\n - `object.save()`\n - `object.delete()`\n\nIn case of trying to save/delete a frozen object, a `FreezeValidationError` will be raised.\nIn case of misconfiguration, a `FreezeConfigurationError` will be raised.\n\n\n### Bypassing\nIf you want to bypass the frozen check for some reason, you can use the contextmanager\n`bypass_fsm_freeze()`, with the freezable object(s) that you want to bypass\nthe checks on, or apply the bypass globally via `bypass_globally` argument.\n\nYou can find some usage example in test `mytest/test_models.py:TestBypassFreezeCheck`.\n\n## Developing\nFor contributors or developers of the project, please see [DEVELOPING.md](docs/DEVELOPING.md)\n\n## Contributing \n(TODO)\nFor anyone who is interested in contributing to this project, please see [CONTRIBUTING.md](docs/CONTRIBUTING.md).\nThank you :)\n\nFor further discussions or suggestions, you could also reach out to me on twitter or email.\n",
    'author': 'ming-tung',
    'author_email': 'mingtung.hong@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ming-tung/django-fsm-freeze',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
