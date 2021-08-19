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
    'version': '0.1.8',
    'description': 'django-fsm data immutability support',
    'long_description': '# django fsm data immutability support\n![CI](https://github.com/ming-tung/django-fsm-freeze/actions/workflows/continues-integration.yml/badge.svg?branch=main)\n[![PyPI version](https://badge.fury.io/py/django-fsm-freeze.svg)](https://badge.fury.io/py/django-fsm-freeze)\n[![Downloads](https://static.pepy.tech/personalized-badge/django-fsm-freeze?period=total&units=international_system&left_color=grey&right_color=yellowgreen&left_text=Downloads)](https://pepy.tech/project/django-fsm-freeze)\n\ndjango-fsm-freeze provides a django model mixin for data immutability based on\n[django-fsm](https://github.com/viewflow/django-fsm).\n\n\n## Installation\n\n```commandline\npip install django-fsm-freeze\n```\n\n## Configuration\n\n- Add `FreezableFSMModelMixin` to your [django-fsm](https://github.com/viewflow/django-fsm) model\n- Specify the `FROZEN_IN_STATES` in which the object should be frozen, meaning the\n  value of its fields/attributes cannot be changed.\n- (optional) Customize the `NON_FROZEN_FIELDS` for mutability\n\nWhen an object is in a frozen state, by default all of its fields are immutable,\nexcept for the `state` field which needs to be mutable for\n[django-fsm](https://github.com/viewflow/django-fsm) to work.\n\nIn case we still want to mutate certain fields when the object is frozen, we can override\nthe `NON_FROZEN_FIELDS` to allow it.\nWhen overriding the `NON_FROZEN_FIELDS`, be careful to include `state` for the reason\nmentioned above.\n\n\n```python\nfrom django.db import models\nfrom django_fsm import FSMField\n\nfrom django_fsm_freeze.models import FreezableFSMModelMixin\n\nclass MyDjangoFSMModel(FreezableFSMModelMixin):\n\n    # In this example, when object is in the \'active\' state, it is immutable.\n    FROZEN_IN_STATES = (\'active\', )\n\n    NON_FROZEN_FIELDS = FreezableFSMModelMixin.NON_FROZEN_FIELDS + (\n        \'a_mutable_field\',\n    )\n\n    # Assign this with the name of the`FSMField` if it is not \'state\'.\n    # If your are using \'state\' as the `FSMField` in your model, you can leave this one out.\n    # See example in `mytest/models.py:FakeModel2`\n    FSM_STATE_FIELD_NAME = \'state\'\n\n    # This field is mutable even when the object is in the frozen state.\n    a_mutable_field = models.BooleanField()\n\n    # django-fsm specifics: state, transitions, etc.\n    # if another name than `state` is chosen, then you need to customize FSM_STATE_FIELD_NAME\n    state = FSMField(default=\'new\')\n    # ...\n\n```\n\nSee configuration example in https://github.com/ming-tung/django-fsm-freeze/blob/main/mytest/models.py\n\n## Usage\n\nThe frozen check takes place when\n - class is prepared (configuration checking)\n - `object.save()`\n - `object.delete()`\n\nIn case of trying to save/delete a frozen object, a `FreezeValidationError` will be raised.\n\n*Note* that in the current design, passing `update_fields` kwarg in `.save()` will bypass the frozen check,\nbecause here we assume it\'s user\'s intention to save the specified fields without trouble/raising error.\n\nSee usage example in tests https://github.com/ming-tung/django-fsm-freeze/blob/main/mytest/test_models.py\n\n# Development\nThis is for contributors or developers of the project.\nThe usual stuff :)\n\n- First, install the package then try to run tests.\n  ```bash\n  # install dependencies from lock file\n  poetry install\n\n  # run checks and tests\n  poetry run flake8 .\n  poetry run isort .\n  poetry run pytest\n  ```\n\n- Whether working on a feature or a bug fix, write meaningful test(s) that fail.\n- Work on the code change\n- Pass the test(s)\n- Review your own work\n- When you are happy, open a Pull Request and ask for review :)\n\n## Make a Release\nFor the owner and contributors, when the time comes, we use github Release (and Actions)\nto publish the package to PyPI.\n\n- In the Release page, start by "Draft a new release"\n- We use semantic versioning and prefix with the letter "v", e.g. "v0.1.7"\n- Choose the target branch (usually `main`) and write a meaningful Release title and description\n- Click on "Publish release" to trigger the CI to automatically publish the package to PyPI\n',
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
