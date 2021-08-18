from typing import Dict, List, SupportsRound, Union
import yaml
import re
import json
from ndd_tools.data_models import BRConfigModel, BoringRegexConfiguration, RegexConfig, RegexFieldModel, RegexPatternModel
from ndd_tools.data_models import EnumStrategy, EnumGroupType
from .logger_mixin import LoggerMixin
from .constants import ARRAY_FIELD




class BoringRegex(LoggerMixin):
    def __init__(self, configuration: BRConfigModel,  **kwargs) -> None:
        self.conf = configuration
        self.set_logger_up(configuration.logger_config)
        self.br_conf: BoringRegexConfiguration = self.load_config_file(configuration.file_path)

    def load_config_file(self, file_path: str) -> BoringRegexConfiguration:
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
            # print(data)
            return BoringRegexConfiguration.parse_obj(data)

    def _get_data_of_path(self, current_path: List[str], input_data: Dict):
        if isinstance(input_data, list) and len(current_path) == 0:
            return input_data
        # print('get_data_of_path', path)
        result = input_data
        for i in current_path:
            result = result[i]
        return result

    def build_field_paths(self, access_paths: List[str], input_data: Dict):
        result_paths = []
        for item in access_paths:
            if len(result_paths) == 0:
                if item == '[...]':
                    data_of_path = self._get_data_of_path([], input_data)
                    for i in range(len(data_of_path)):
                        result_paths.append([i])
                else:
                    result_paths.append([item])
            else:
                if item == '[...]':
                    # print('current result paths ', result_paths)
                    deleted_rpaths = []
                    new_paths = []
                    for rpath in result_paths:
                        data_of_path = self._get_data_of_path(rpath, input_data)
                        # print('check path', rpath, data_of_path)
                        for i in range(len(data_of_path)):
                            new_path = rpath + [i]
                            new_paths.append(new_path)
                            # print('\t\tnew path', new_path)
                        deleted_rpaths.append(rpath)
                    for np in new_paths:
                        result_paths.append(np)
                    for dp in deleted_rpaths:
                        result_paths.remove(dp)
                else:
                    for rpath in result_paths:
                        rpath.append(item)
        return result_paths

    def find_field_values(self, access_path: List[str], input_data: Dict) -> List[str]:
        paths = self.build_field_paths(access_path, input_data)
        final_result = []
        for path in paths:
            temp_result = input_data
            for item in path:
                temp_result = temp_result[item]
            final_result.append(temp_result)
        return final_result

    def handle_strategy(self, source: str, field_conf: RegexFieldModel):
        # print('handle source ', source, ' with ', field_conf)
        # return "OK, i hope so"
        if field_conf.strategy == EnumStrategy.GETALL:
            return {'result': source, 'source': source}

        if field_conf.strategy == EnumStrategy.MATCH:
            return {'result': self._execute_match(source, field_conf.patterns), 'source': source}

        if field_conf.strategy == EnumStrategy.SEARCH:
            return {'result': self._execute_search(source, field_conf.patterns), 'source': source}

        if field_conf.strategy == EnumStrategy.FINDALL:
            return {'result': self._execute_findall(source, field_conf.patterns), 'source': source}

        if field_conf.strategy == EnumStrategy.FINDITER:
            return {'result': self._execute_finditer(source, field_conf.patterns), 'source': source}

        raise ValueError('strategy must provide')

    def process_data(self, data: Dict, config: RegexConfig):
        result = {}
        for field in config.regex_fields:
            source_strings = self.find_field_values(field.field, data)
            # print('source', source_strings)
            result[field.key] = [self.handle_strategy(source, field) for source in source_strings]
        return result

    def _execute_match(self, data: str, patterns: List[RegexPatternModel]):
        for pattern in patterns:
            try:
                result = re.match(r'%s' % pattern.value, data, flags=re.I)
                if pattern.group_type == EnumGroupType.GROUPDICT:
                    return [i.groupdict() for i in result]
                if pattern.group_type == EnumGroupType.GROUP:
                    return "finditer not support group yet"
                if pattern.group_type == EnumGroupType.GROUPS:
                    return "finditer not support groups yet"

            except Exception as e:
                pass

    def _execute_search(self, data: str, patterns: List[RegexPatternModel]):
        # print('_execute_search', data)
        for pattern in patterns:
            # print('_execute_search', pattern)
            try:
                result = re.search(r'%s' % pattern.value, data, flags=re.I)
                # print('_execute_search result', result)
                if pattern.group_type == EnumGroupType.GROUPDICT:
                    return [i.groupdict() for i in result]
                if pattern.group_type == EnumGroupType.GROUP:
                    _r = []
                    for index in pattern.group_indexes:
                        _r.append(result.group(index))
                    if not _r:
                        continue
                    return _r
                if pattern.group_type == EnumGroupType.GROUPS:
                    return result.groups()
            except IndexError as e:
                raise e
            except Exception as e:
                # print('get exception ', e)
                pass

    def _execute_findall(self, data: str, patterns: List[RegexPatternModel]):
        # print('_execute_findall', data)
        for pattern in patterns:
            try:
                # print('_execute_findall pattern ', pattern)
                return re.findall(r'%s' % pattern.value, data, flags=re.I)
            except IndexError as e:
                raise e
            except Exception as e:
                pass

    def _execute_finditer(self, data: str, patterns: List[RegexPatternModel]):
        for pattern in patterns:
            try:
                result = re.finditer(r'%s' % pattern.value, data, flags=re.I)
                if pattern.group_type == EnumGroupType.GROUPDICT:
                    return [i.groupdict() for i in result]
                if pattern.group_type == EnumGroupType.GROUP:
                    return "finditer not support group yet"
                if pattern.group_type == EnumGroupType.GROUPS:
                    return "finditer not support groups yet"
            except IndexError as e:
                raise e
            except Exception as e:
                pass
    
    def run(self, input_data: Dict = None, config_name: str = None):
        config: RegexConfig = self.br_conf.config.get(config_name)
        return self.process_data(input_data, config)
