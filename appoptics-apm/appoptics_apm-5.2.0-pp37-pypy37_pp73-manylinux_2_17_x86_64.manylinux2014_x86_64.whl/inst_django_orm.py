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
""" AppOptics APM instrumentation for Django ORM.
"""
import logging
import re

from appoptics_apm import config, util

logger = logging.getLogger(__name__)


def wrap_execute(func, f_args, f_kwargs, res):
    obj, sql = f_args[:2]
    kwargs = {}
    log_sql_args = not config.get('enable_sanitize_sql', True) and len(f_args) > 2
    if log_sql_args:
        kwargs['QueryArgs'] = str(f_args[2]).encode('utf-8')

    kwargs['Query'] = sql.encode('utf-8')
    if 'NAME' in obj.db.settings_dict:
        kwargs['Database'] = obj.db.settings_dict['NAME']
    if 'HOST' in obj.db.settings_dict:
        kwargs['RemoteHost'] = obj.db.settings_dict['HOST']
    if 'ENGINE' in obj.db.settings_dict:
        if re.search('post', obj.db.settings_dict['ENGINE']):
            kwargs['Flavor'] = 'postgresql'
        elif re.search('sqlite', obj.db.settings_dict['ENGINE']):
            kwargs['Flavor'] = 'sqlite'
        elif re.search('mysql', obj.db.settings_dict['ENGINE']):
            kwargs['Flavor'] = 'mysql'
        elif re.search('oracle', obj.db.settings_dict['ENGINE']):
            kwargs['Flavor'] = 'oracle'
    return kwargs


class CursorAppOpticsApmWrapper:
    ###########################################################################
    # Django cursors can be wrapped arbitrarily deeply with the following API.
    # Each class contains a references to the DB object, and the next level
    # cursor. Control passes to the cursor in execute and executemany, wrapped
    # with whatever behavior the wrapper provides.
    ###########################################################################

    def __init__(self, cursor, db):
        self.cursor = cursor
        self.db = db

    def __getattr__(self, attr):
        if attr in self.__dict__:
            return self.__dict__[attr]
        else:
            return getattr(self.cursor, attr)

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def __iter__(self):
        return iter(self.cursor)

    def execute(self, sql, params=None):
        if params is None:
            return self.cursor.execute(sql)
        else:
            return self.cursor.execute(sql, params)

    def executemany(self, sql, param_list):
        return self.cursor.executemany(sql, param_list)


def wrap(module):
    try:
        cursor_method = module.BaseDatabaseWrapper.cursor
        if getattr(cursor_method, '_appoptics_apm_wrapped', False):
            return

        appoptics_apm_wrapper = util.log_method(
            'djangoORM', callback=wrap_execute, store_backtrace=util._collect_backtraces('django_orm'))
        setattr(CursorAppOpticsApmWrapper, 'execute', appoptics_apm_wrapper(CursorAppOpticsApmWrapper.execute))
        setattr(CursorAppOpticsApmWrapper, 'executemany', appoptics_apm_wrapper(CursorAppOpticsApmWrapper.executemany))

        def cursor_wrap(self):
            try:
                return CursorAppOpticsApmWrapper(cursor_method(self), self)
            except Exception as e:
                logger.error("[AppOptics] Error in cursor_wrap: %s" % e)
                # need to re-raise application exceptions thrown here
                raise

        cursor_wrap._appoptics_apm_wrapped = True

        setattr(module.BaseDatabaseWrapper, 'cursor', cursor_wrap)
    except Exception as e:
        logger.error("[AppOptics] Error in module_wrap: %s" % e)
