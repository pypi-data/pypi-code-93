# -*- coding: utf-8 -*-
# @Time    : 2021-03-25 09:40
# @Author  : xzr
# @File    : test_json_dumps
# @Software: PyCharm
# @Contact : xzregg@gmail.com
# @Desc    :
from unittest import TestCase
from . import BaseTestCase
from faker import Faker

fake = Faker()


class TestJson_dumps(BaseTestCase):

    def test_json_dumps(self):
        from ..utils import json_dumps, json_loadsobj
        from ..serializer import DataSerializer, s
        from myadmin.models import User
        u:User = User.create_root()



        qs = User.objects.all()[0]
        print(json_loadsobj(json_dumps(qs)))
        self.assertEqual(u.username, json_loadsobj(json_dumps(qs)).username)

        test_d = fake.pydict()
        json_test_d = json_dumps(test_d)
        j_obj = json_loadsobj(json_test_d)
        self.assertEqual(test_d.keys(), j_obj.keys())

        class TestSer(DataSerializer):
            f1 = s.CharField(max_length=20)
            f2 = s.IntegerField()

        a = TestSer()
        a.o.f1 = '2'
        a.o.f2 = 3
        self.assertEqual(a.o.f1, json_loadsobj(json_dumps(a)).f1)
        print(json_test_d)
        print(json_dumps(a))
