'''
    Copyright 2018 SerialLab, CORP

    This file is part of SerialBox.

    SerialBox is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    SerialBox is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with SerialBox.  If not, see <http://www.gnu.org/licenses/>.
'''
from django.conf import settings

SB_POOL_API_LIST_LIMIT = getattr(settings, 'SB_POOL_API_LIST_LIMIT', 1000)

GENERATOR_PREPROCESSING_RULES = getattr(
    settings,
    'GENERATOR_PREPROCESSING_RULES',
    {
        'default': [
            'serialbox.rules.limits.ActiveRule',
            'serialbox.rules.limits.RequestThresholdLimitRule',
        ],
        'serialbox.generators.sequential.SequentialGenerator': [
            'serialbox.rules.limits.ActiveRule',
            'serialbox.rules.limits.SizeLimitRule',
            'serialbox.rules.limits.RequestThresholdLimitRule',
        ]
    })

GENERATOR_POSTPROCESSING_RULES = getattr(
    settings,
    'GENERATOR_POSTPROCESSING_RULES',
    {})

REST_FRAMEWORK = getattr(settings, 'REST_FRAMEWORK', {})
REST_FRAMEWORK.update({
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
        'rest_framework.renderers.BrowsableAPIRenderer',
        'rest_framework_xml.renderers.XMLRenderer',
        'rest_framework_csv.renderers.CSVRenderer',
    ),
    'DEFAULT_PARSER_CLASSES': (
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework_xml.parsers.XMLParser',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    )
})
