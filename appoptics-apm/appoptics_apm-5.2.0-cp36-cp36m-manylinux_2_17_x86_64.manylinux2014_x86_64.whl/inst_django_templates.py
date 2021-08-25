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
""" AppOptics APM instrumentation for Django's template system
"""
import logging

from appoptics_apm import util

logger = logging.getLogger(__name__)

TEMPLATE_LAYER = 'template'


def before_render_cb(func, f_args, f_kwargs):
    """ Callback to django.template.base.Template.render(),
        retrieves template name from Template object and
        manually turns a log_method into a profile_function,
        (necessary to dynamically generate profile name...) """
    template_name = f_args[0].name
    keys = {
        'Language': 'template',
        'ProfileName': template_name,
    }
    return f_args, f_kwargs, keys


def after_render_cb(func, f_args, f_kwargs, ret):
    template_name = f_args[0].name
    keys = {
        'Language': 'template',
        'ProfileName': template_name,
    }
    return keys, None


def wrap(module):
    try:
        # profile on specific template name (inner wrap)
        profile_wrapper_render = util.log_method(None, before_callback=before_render_cb, callback=after_render_cb)

        # overall template layer (outer wrap)
        layer_wrapper_render = util.log_method(TEMPLATE_LAYER)

        setattr(module.Template, 'render', layer_wrapper_render(profile_wrapper_render(module.Template.render)))

    except Exception as e:
        logger.error("AppOptics APM error: %s" % str(e))
