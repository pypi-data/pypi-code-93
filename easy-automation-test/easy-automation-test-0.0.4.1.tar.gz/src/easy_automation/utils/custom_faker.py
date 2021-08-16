#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# @author: James Zhang
# @data  : 2021/7/15
from typing import Iterable

from faker import Faker


class CustomFaker:

    def __init__(self, locale='en_US'):
        '''
        :param locale: support most language, 'zh_CN', 'de_DE', ...
        '''
        self._faker = Faker(locale=locale)

    @property
    def faker(self):
        return self._faker

    def __getattr__(self, item):
        return getattr(self.faker, item)()

    @property
    def username(self):
        return self.faker.name()

    @property
    def first_name(self):
        return self.faker.first_name()

    @property
    def last_name(self):
        return self.faker.last_name()

    def password(self, limit=3):
        '''
        mini length is 4
        '''
        if limit <= 3:
            return self.faker.password()
        else:
            return self.faker.password(length=limit)

    @property
    def file_name(self):
        return self.faker.file_name()

    @property
    def file_path(self):
        return self.faker.file_path()

    def number(self, min=0, max=9999):
        return self.faker.random_int(min=min, max=max)

    @property
    def word(self):
        return self.faker.word()

    @property
    def words(self):
        return ' '.join(self.faker.words())


if __name__ == '__main__':
    test = CustomFaker()
    print(test.words)

