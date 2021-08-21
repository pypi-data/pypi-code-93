# -*- coding: utf-8 -*-

"""
Flask-based API development framework in Python

GitHub: https://github.com/alph4ice/mach4/
PyPI: https://pypi.org/project/mach4/

Copyright 2021 Cyriaque Perier

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from flask import request
from .response import *
from .refresh import *
from .pipeline import API
from .pipeline import MACH4_VERSION

__version__ = MACH4_VERSION