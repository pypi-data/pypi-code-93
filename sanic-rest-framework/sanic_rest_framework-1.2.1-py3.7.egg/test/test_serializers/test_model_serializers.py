"""
@Author：WangYuXiang
@E-mile：Hill@3io.cc
@CreateTime：2021/3/8 11:59
@DependencyLibrary：无
@MainFunction：无
@FileDoc： 
    test_model_serializers.py
    文件说明
@ChangeHistory:
    datetime action why
    example:
    2021/3/8 11:59 change 'Fix bug'
        
"""
import asyncio
import uuid
from datetime import datetime

from tortoise.contrib.test import initializer, TestCase, finalizer

from test.models import TestModel, TestOneToOneModel, CharEnum, Enum1
from srf.serializers import ModelSerializer


class TestModelSerializer(ModelSerializer):
    class Meta:
        model = TestModel
        # fields = ('char_field',)
        exclude = ('id',)
        read_only_fields = ('char_field',)
        write_only_fields = ('float_field',)


initializer(['test.models'])


class TestOrdinarySerializer(TestCase):
    def setUp(self) -> None:
        self.data = {
            'char_field': '老四',
            'float_field': 1.36,
            'date_field': '2016-11-1',
            'int_field': 999,
            'decimal_field': 999.9,
            'datetime_field': '2016-12-1 11:1:1',
            'int_enum_field': 1,
            'char_enum_field': '好',
            'boolean_field': False,
            'small_int_field': 1,
            'big_int_field': 99999,
            'text_field': 'PE',
            'json_field': '{"a":1}',
            'uuid_field': '91a4c540-80b5-11eb-b03f-e0d55e47dfb2',
            'one_to_many': [],
            'one_to_one': {},
            'many_to_many': [],
        }

    async def test_serializer(self):
        # for name, field in UserModel._meta.fields_map.items():
        #     ModelConverter().convert(TestModelSerializer, field, name)

        tm = TestModel()
        tm.char_field = 1
        tm.float_field = 1
        tm.date_field = '2016-11-11'
        tm.int_field = 1
        tm.decimal_field = 1
        tm.datetime_field = datetime(2016, 11, 11, 0, 0, 0)
        tm.int_enum_field = Enum1.OK
        tm.char_enum_field = CharEnum.OK
        tm.boolean_field = True
        tm.small_int_field = 1
        tm.big_int_field = 1
        tm.text_field = '1'
        tm.json_field = {}
        tm.uuid_field = str(uuid.uuid1())
        tm.one_to_one = await TestOneToOneModel(name='1').save()
        await tm.save()
        tms = TestModelSerializer(instance=await TestModel.all(), many=True)
        print(await tms.data)
        tms = TestModelSerializer(data=self.data, partial=True)
        await tms.is_valid()
        print(tms.validated_data)
        print(tms.fields)

    @classmethod
    async def tearDownClass(cls) -> None:
        finalizer()
