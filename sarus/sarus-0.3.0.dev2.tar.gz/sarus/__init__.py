"""Copyright 2020 Sarus SAS.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Sarus library to leverage sensitive data without revealing them

This lib contains classes and method to browse,
learn from & explore sensitive datasets.
It connects to a Sarus server, which acts as a gateway, to ensure no
results/analysis coming out of this lib are sensitive.
"""
from .sarus import Client, Dataset  # noqa: F401

VERSION = "0.3.0-dev2"
