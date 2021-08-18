from datetime import date
from enum import Enum, IntEnum

from tortoise import fields
from tortoise import Model
from tortoise.fields import ForeignKeyRelation, ReverseRelation


class Enum1(IntEnum):
    OK = 1
    BAD = 2


class CharEnum(Enum):
    OK = '好'
    BAD = '坏'


class TestModel(Model):
    char_field = fields.CharField(max_length=8, null=True)
    float_field = fields.FloatField()
    date_field = fields.DateField()
    int_field = fields.IntField()
    decimal_field = fields.DecimalField(max_digits=13, decimal_places=3)
    datetime_field = fields.DatetimeField()
    int_enum_field = fields.IntEnumField(enum_type=Enum1)
    char_enum_field = fields.CharEnumField(enum_type=CharEnum)
    boolean_field = fields.BooleanField()
    small_int_field = fields.SmallIntField()
    big_int_field = fields.BigIntField()
    text_field = fields.TextField()
    json_field = fields.JSONField()
    uuid_field = fields.UUIDField()
    one_to_many: ForeignKeyRelation["TestManyToOneModel"] = fields.ForeignKeyField('models.TestManyToOneModel', related_name='many_to_one', null=True)
    one_to_one: fields.OneToOneRelation["TestOneToOneModel"] = fields.OneToOneField('models.TestOneToOneModel', related_name='one_to_one', null=True)
    many_to_many: fields.ManyToManyRelation["TestModel"] = fields.ManyToManyField("models.ManyToManyModel", related_name="many_2_many", through="many_many", null=True)


class TestOneTOManyModel(Model):
    one_to_many: ForeignKeyRelation["TestModel"] = fields.ForeignKeyField('models.TestModel', related_name='many_to_one')


class TestManyToOneModel(Model):
    many_to_one: fields.ReverseRelation["TestModel"]


class TestOneToOneModel(Model):
    name = fields.CharField(max_length=8, null=True)


class ManyToManyModel(Model):
    many_2_many: fields.ManyToManyRelation["TestModel"]


class UserModel(Model):
    name = fields.CharField(max_length=8, null=False)
    birthday = fields.DateField()
    phone = fields.CharField(max_length=11)
    balance = fields.DecimalField(13, 3)
    address: fields.ManyToManyRelation["AddressModel"] = fields.ManyToManyField(
        'models.AddressModel', through='user2address', related_name='user', null=True)


class AddressModel(Model):
    phone = fields.CharField(12, null=False)
    address = fields.CharField(100)
    house_number = fields.CharField(100)
    # user: fields.ManyToManyRelation[UserModel]


class SchoolModel(Model):
    name = fields.CharField(12)
    address: fields.OneToOneRelation["AddressModel"] = fields.OneToOneField("models.AddressModel", 'school')


class ClassRoomModel(Model):
    room_number = fields.CharField(18)
    student_count = fields.IntField()
    students: ReverseRelation['StudentModel']


class StudentModel(Model):
    name = fields.CharField(max_length=12, null=False)
    class_room: ForeignKeyRelation["ClassRoomModel"] = fields.ForeignKeyField('models.ClassRoomModel', 'students')


class DateSeriesModel(Model):
    name = fields.TimeDeltaField()
