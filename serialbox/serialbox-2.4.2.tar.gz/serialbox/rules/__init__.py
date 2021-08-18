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
import logging
import importlib
from serialbox import serialbox_settings as settings

logger = logging.getLogger("rules")


def load_rules_from_list(rule_list):
    '''
    Returns a list of rule class instances based a list of supplied strings.
    '''
    logging.debug('Loading rule list %s', rule_list)
    rule_classes = []
    for rule in rule_list:
        mod_func = rule.rsplit('.', 1)
        mod = importlib.import_module(mod_func[0])
        cls = getattr(mod, mod_func[1])
        rule_classes.append(cls())
    return rule_classes


def get_rules(generator_instance, settings_dict, use_default=True):
    '''
    Looks up the processing rules for the supplied generator instance,
    loads the instances into memory and returns them as a list of classes
    '''
    gc_name = generator_instance.__module__ + '.' + \
              generator_instance.__class__.__name__
    rules = settings_dict or {}
    logger.debug('Getting processor list for generator %s using dictionary %s',
                 gc_name, rules)
    rule_list = rules.get(gc_name) or rules.get('default', [])
    return load_rules_from_list(rule_list)


def get_preprocessing_rules(generator_instance, settings_module=None):
    generator_settings = settings_module or settings
    return get_rules(generator_instance,
                     generator_settings.GENERATOR_PREPROCESSING_RULES) or {}


def get_postprocessing_rules(generator_instance, settings_module=None):
    generator_settings = settings_module or settings
    return get_rules(generator_instance,
                     generator_settings.GENERATOR_POSTPROCESSING_RULES) or {}
