#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/7/14
import os

import yaml

from easy_automation.utils.common import Singleton, FrozenJson, find_project_root_dir

class YamlLoader(metaclass=Singleton):
    _yaml_file_loader = {}

    def __init__(self, yaml_file: str):
        '''
        yaml_file should only pass file name under testdata directory
        :param yaml_file:
        '''
        yaml_file = os.path.join(find_project_root_dir(), 'testdata', yaml_file)
        if not (yaml_file.endswith('.yaml') or yaml_file.endswith('.yml')):
            raise TypeError('Only support parse yaml format file.')
        if not os.path.isfile(yaml_file):
            raise FileNotFoundError(f'No such file or directory: {yaml_file}')

        if yaml_file not in self._yaml_file_loader:
            with open(yaml_file, 'r', encoding='utf-8') as fp:
                self._yaml_file_loader[yaml_file] = yaml.safe_load(fp)

        self._yaml_loader = self._yaml_file_loader[yaml_file]
        self._data = FrozenJson(self._yaml_loader)

    @property
    def data(self):
        '''
        access data through properties.
        :return:
        '''
        return self._data

    def get(self, args):
        return self._yaml_loader.get(args)

    def __getitem__(self, args):
        return self._yaml_loader[args]





if __name__ == '__main__':
    test = YamlLoader('account_test.yaml')
    test2 = YamlLoader('account_test.yaml')
    test3 = YamlLoader('account_test.yaml')
    print(test is test2)
    print(test2 is test3)
    print(test.data.test_account[1].name)
    print(test['test_account'][0]['name'])
    print(test.get('test_account')[0].get('name'))

