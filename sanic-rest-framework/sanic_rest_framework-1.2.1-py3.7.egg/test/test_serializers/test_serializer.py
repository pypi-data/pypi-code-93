"""
@Author：WangYuXiang
@E-mile：Hill@3io.cc
@CreateTime：2021/1/27 9:55
@DependencyLibrary：无
@MainFunction：无
@FileDoc：
    test_serializer.py
    测试文件
@ChangeHistory:
    datetime action why
    example:
    2021/1/27 9:55 change 'Fix bug'

"""
import datetime
import unittest
from collections import OrderedDict
from copy import deepcopy
from decimal import Decimal

from srf.fields import (
    CharField, IntegerField, DateField, DecimalField)
from srf.serializers import Serializer

from tortoise.contrib.test import initializer, finalizer, TestCase
from test.models import UserModel, AddressModel, SchoolModel, StudentModel, ClassRoomModel


class AddressSerializer(Serializer):
    phone = CharField(max_length=11, required=True)
    address = CharField(max_length=100)
    house_number = CharField(max_length=100)


class UserSerializer(Serializer):
    name = CharField(max_length=8, required=True)
    birthday = DateField()
    phone = CharField(max_length=11)
    balance = DecimalField(13, 3)
    address = AddressSerializer(many=True)


class SchoolSerializer(Serializer):
    name = CharField(max_length=12)
    address = AddressSerializer()


class StudentSerializer(Serializer):
    name = CharField(max_length=12)
    # class_room = ClassRoomSerializer()


class ClassRoomSerializer(Serializer):
    room_number = CharField(max_length=12)
    student_count = IntegerField()
    students = StudentSerializer(many=True)


class M2OClassRoomSerializer(Serializer):
    room_number = CharField(max_length=12)
    student_count = IntegerField()


class M2OStudentSerializer(Serializer):
    name = CharField(max_length=12)
    class_room = M2OClassRoomSerializer()


initializer(['test.models'])


class TestOrdinarySerializer(TestCase):
    def setUp(self) -> None:
        self.mapping_data = {
            'phone': '17674707036',
            'address': '长沙市IFS',
            'house_number': '67L'
        }
        self.res = OrderedDict(self.mapping_data)

    async def test_serializer(self):
        """测试序列化"""
        addr_model = AddressModel(**self.mapping_data)
        await addr_model.save()
        as_map = AddressSerializer(instance=self.mapping_data)
        as_model = AddressSerializer(instance=await AddressModel.get(pk=1))
        self.assertEqual(await as_map.data, self.res)
        self.assertEqual(await as_model.data, self.res)

    async def test_deserializer(self):
        """测试反序列化"""

        addr_model = AddressModel(**self.mapping_data)
        await addr_model.save()
        as_map = AddressSerializer(data=self.mapping_data)
        as_model = AddressSerializer(data=await AddressModel.get(pk=1))
        self.assertIs(await as_map.is_valid(), True)
        self.assertEqual(as_map.validated_data, self.res)

        self.assertIs(await as_model.is_valid(), False)
        print(as_model.errors)
        # print(as_model.validated_data)

    @classmethod
    async def tearDownClass(cls) -> None:
        finalizer()


class TestM2MNestedSerializer(TestCase):
    """测试多对多嵌套"""

    def setUp(self) -> None:
        self.mapping_data = {
            'name': '老四',
            'birthday': '2010-11-16',
            'phone': '17674707037',
            'balance': '99.009',
            'address': [{
                'phone': '17674707036',
                'address': '长沙市IFS',
                'house_number': '67L'
            }, {
                'phone': '17674707037',
                'address': '长沙市HPT',
                'house_number': '4L'
            }]
        }
        self.des_res = OrderedDict({'name': '老四', 'birthday': datetime.date(2010, 11, 16),
                                    'phone': '17674707037', 'balance': Decimal('99.009'),
                                    'address': [
                                        OrderedDict({'phone': '17674707036', 'address': '长沙市IFS', 'house_number': '67L'}),
                                        OrderedDict({'phone': '17674707037', 'address': '长沙市HPT', 'house_number': '4L'})]})
        self.s_res = OrderedDict({'name': '老四', 'birthday': '2010-11-16',
                                  'phone': '17674707037', 'balance': Decimal('99.009'),
                                  'address': [
                                      OrderedDict({'phone': '17674707036', 'address': '长沙市IFS', 'house_number': '67L'}),
                                      OrderedDict({'phone': '17674707037', 'address': '长沙市HPT', 'house_number': '4L'})]})
        self.res = OrderedDict(self.mapping_data)

    async def test_serializer(self):
        """测试序列化"""
        user_info = deepcopy(self.mapping_data)
        address = user_info.pop('address')
        user = UserModel(**user_info)
        await user.save()
        for i in address:
            addr = AddressModel(**i)
            await addr.save()
            await user.address.add(addr)

        us_map = UserSerializer(instance=self.mapping_data)
        us_model = UserSerializer(instance=await UserModel.get(pk=1))
        print(await us_model.data)
        self.assertEqual(await us_map.data, self.s_res)
        self.assertEqual(await us_model.data, self.s_res)

    async def test_deserializer(self):
        """测试反序列化"""
        user_info = deepcopy(self.mapping_data)
        address = user_info.pop('address')
        user = UserModel(**user_info)
        await user.save()
        for i in address:
            addr = AddressModel(**i)
            await addr.save()
            await user.address.add(addr)
        us_map = UserSerializer(data=self.mapping_data)
        us_model = UserSerializer(data=await UserModel.get(pk=1))
        self.assertIs(await us_map.is_valid(), True)
        self.assertEqual(us_map.validated_data, self.des_res)

        self.assertIs(await us_model.is_valid(), False)
        print(us_model.errors)

    @classmethod
    async def tearDownClass(cls) -> None:
        finalizer()


class TestO2OSerializer(TestCase):
    """测试一对一序列化"""

    def setUp(self) -> None:
        self.mapping_data = {
            'name': '老四',
            'address': {
                'phone': '17674707036',
                'address': '长沙市IFS',
                'house_number': '67L'
            }
        }
        self.res = OrderedDict(self.mapping_data)

    async def test_serializer(self):
        """测试序列化"""
        school_info = deepcopy(self.mapping_data)
        address = school_info.pop('address')
        address_model = await AddressModel.create(**address)
        school_model = await SchoolModel.create(address=address_model, **school_info)

        ss_map = SchoolSerializer(instance=self.mapping_data)
        us_model = SchoolSerializer(instance=await SchoolModel.get(pk=1))
        self.assertEqual(await ss_map.data, self.res)
        self.assertEqual(await us_model.data, self.res)

    async def test_deserializer(self):
        """测试反序列化"""
        school_info = deepcopy(self.mapping_data)
        address = school_info.pop('address')
        address_model = await AddressModel.create(**address)
        school_model = await SchoolModel.create(address=address_model, **school_info)

        ss_map = SchoolSerializer(data=self.mapping_data)
        ss_model = SchoolSerializer(data=await SchoolModel.get(pk=1))
        self.assertIs(await ss_map.is_valid(), True)
        self.assertEqual(ss_map.validated_data, self.res)

        self.assertIs(await ss_model.is_valid(), False)
        print(ss_model.errors)

    @classmethod
    async def tearDownClass(cls) -> None:
        finalizer()


class TestO2MSerializer(TestCase):
    """测试一对多序列化器"""

    def setUp(self) -> None:
        self.mapping_data = {
            'room_number': '1024',
            'student_count': 80,
            'students': [{'name': '刘文静'}, {'name': '马冬梅'}, {'name': '光明'}]
        }
        self.res = OrderedDict(self.mapping_data)

    async def test_serializer(self):
        """测试序列化"""

        class_room_info = deepcopy(self.mapping_data)
        students = class_room_info.pop('students')
        class_model = await ClassRoomModel.create(**class_room_info)
        await StudentModel.bulk_create([StudentModel(class_room=class_model, **student) for student in students])

        cs_map = ClassRoomSerializer(instance=self.mapping_data)
        cs_model = ClassRoomSerializer(instance=class_model)
        print(await cs_map.data)
        print(await cs_model.data)
        self.assertEqual(await cs_map.data, self.res)
        self.assertEqual(await cs_model.data, self.res)

    async def test_deserializer(self):
        """测试反序列化"""
        class_room_info = deepcopy(self.mapping_data)
        students = class_room_info.pop('students')
        class_model = await ClassRoomModel.create(**class_room_info)
        await StudentModel.bulk_create([StudentModel(class_room=class_model, **student) for student in students])

        cs_map = ClassRoomSerializer(data=self.mapping_data)
        cs_model = ClassRoomSerializer(data=class_model)
        self.assertIs(await cs_map.is_valid(), True)
        self.assertEqual(cs_map.validated_data, self.res)

        self.assertIs(await cs_model.is_valid(), False)
        print(cs_model.errors)

    @classmethod
    async def tearDownClass(cls) -> None:
        finalizer()


class TestM2OSerializer(TestCase):
    """测试多对一序列化器"""

    def setUp(self) -> None:
        self.mapping_data = [
            {
                'name': '马冬梅',
                'class_room': {
                    'room_number': '1024',
                    'student_count': 40
                }
            }, {
                'name': '光明',
                'class_room': {
                    'room_number': '1024',
                    'student_count': 40
                }
            }, {
                'name': '李焕英',
                'class_room': {
                    'room_number': '1024',
                    'student_count': 40
                }
            },

        ]
        self.res_dict = {
            '马冬梅': {
                'name': '马冬梅',
                'class_room': {
                    'room_number': '1024',
                    'student_count': 40
                }
            }, '光明': {
                'name': '光明',
                'class_room': {
                    'room_number': '1024',
                    'student_count': 40
                }
            }, '李焕英': {
                'name': '李焕英',
                'class_room': {
                    'room_number': '1024',
                    'student_count': 40
                }
            },
        }
        self.res = OrderedDict(self.mapping_data)

    async def test_serializer(self):
        """测试序列化"""

        student_model_list = []
        students = deepcopy(self.mapping_data)
        # 初始化数据库数据
        for student_info in students:
            class_room_info = student_info.pop('class_room')
            class_room_model, status = await ClassRoomModel.get_or_create(**class_room_info)
            student_model = await StudentModel.create(class_room=class_room_model, **student_info)
            student_model_list.append(student_model)

        # 验证模型类型的数据是否正常
        for student_model in student_model_list:
            m2oss_model = M2OStudentSerializer(instance=student_model)
            self.assertEqual(await m2oss_model.data, OrderedDict(self.res_dict[student_model.name]))

        # 验证字段类型的数据是否正常
        students = deepcopy(self.mapping_data)
        for student_info in students:
            m2oss_map = M2OStudentSerializer(instance=student_info)
            self.assertEqual(await m2oss_map.data, OrderedDict(self.res_dict[student_info['name']]))

    async def test_deserializer(self):
        """测试反序列化"""
        student_model_list = []
        students = deepcopy(self.mapping_data)
        # 初始化数据库数据
        for student_info in students:
            class_room_info = student_info.pop('class_room')
            class_room_model, status = await ClassRoomModel.get_or_create(**class_room_info)
            student_model = await StudentModel.create(class_room=class_room_model, **student_info)
            student_model_list.append(student_model)

        # 验证模型类型的数据是否正常
        for student_model in student_model_list:
            m2oss_model = M2OStudentSerializer(data=student_model)
            self.assertIs(await m2oss_model.is_valid(), False)
            print(m2oss_model.errors)

        # 验证字段类型的数据是否正常
        students = deepcopy(self.mapping_data)
        for student_info in students:
            m2oss_map = M2OStudentSerializer(data=student_info)
            self.assertIs(await m2oss_map.is_valid(), True)
            self.assertEqual(m2oss_map.validated_data, OrderedDict(self.res_dict[student_info['name']]))

    @classmethod
    async def tearDownClass(cls) -> None:
        finalizer()


if __name__ == '__main__':
    unittest.main()
