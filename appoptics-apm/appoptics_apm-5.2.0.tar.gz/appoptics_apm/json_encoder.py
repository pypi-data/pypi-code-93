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
""" Handles JSON conversion for various object types that may be found in queries
"""
try:
    import json
except ImportError:
    import simplejson as json

import datetime

from bson.dbref import DBRef
from bson.objectid import ObjectId


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ObjectId) or isinstance(obj, DBRef):
            return str(obj)
        elif isinstance(obj, datetime.datetime):
            return obj.strftime('%Y-%m-%dT%H:%M:%S')
        else:
            try:
                return json.JSONEncoder.default(self, obj)
            except Exception:
                # so we don't fail the request:
                return "[unsupported type %s]" % (type(obj))
