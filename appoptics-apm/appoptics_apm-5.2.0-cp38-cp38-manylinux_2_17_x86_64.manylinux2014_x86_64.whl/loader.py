#    Copyright 2021 SolarWinds, LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
""" AppOptics APM instrumentation loader

Checks appoptics_apm.config['inst_enabled'] and imports as requested. used by middleware
and djangoware.
"""
import appoptics_apm


def _enabled(m):
    return appoptics_apm.config['inst_enabled'][m]


def load_inst_modules():
    # TODO_Pylint: Check if disabling warnings here is good
    # pylint: disable-msg=W0611
    if _enabled('memcache'):
        from appoptics_apm import inst_memcache
    if _enabled('pymongo'):
        from appoptics_apm import inst_pymongo
    if _enabled('sqlalchemy'):
        from appoptics_apm import inst_sqlalchemy
    if _enabled('httplib'):
        from appoptics_apm import inst_httplib
    if _enabled('redis'):
        from appoptics_apm import inst_redis
    # additionally, in djangoware.py: 'django_orm', 'django_templates'
