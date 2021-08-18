"""
@Author: WangYuXiang
@E-mile: Hill@3io.cc
@CreateTime: 2021/3/15 19:45
@DependencyLibrary: 无
@MainFunction：无
@FileDoc:
    test_otm_mto.py
    文件描述
@ChangeHistory:
    datetime action why
    example:
    2021/2/4 14:35 change 'Fix bug'
        
"""

from tortoise import Model, Tortoise, run_async
from tortoise import fields


class ClassRoom(Model):
    class_num = fields.IntField()
    class_name = fields.CharField(128)
    students = fields.ReverseRelation['Students']


class Students(Model):
    name = fields.CharField(30)
    class_room: fields.ForeignKeyRelation[ClassRoom] = fields.ForeignKeyField('models.ClassRoom', 'students',
                                                                              null=True)


async def run():
    await Tortoise.init(db_url="sqlite::memory:", modules={"models": ["__main__"]})
    await Tortoise.generate_schemas()

    # 测试正向创建
    cr = await ClassRoom.create(**{
        'class_num': 1,
        'class_name': '1000'
    })
    std = Students(name='刘桂香', class_room=cr)
    await std.save()
    cr = await ClassRoom.create(**{
        'class_num': 1,
        'class_name': '1000'
    })
    print(await cr.students)
    std = Students(name='刘桂香')
    std.class_room = cr
    await std.save()
    # 结论多对一关系和一对多关系都只能由单边发起
    # 列如在 Students 类中设置了多对一关系，那么必须先创建对应的 ClassRoom 然后才能创建 Students
    # 在 Students.class_room 允许为空的情况下，可以先创建 Students 再创建 ClassRoom
    # 先创建 Students 再创建 ClassRoom ,如果需要关联多对一那么只能 Students.class_room=ClassRoom,
    # 不可以 ClassRoom.students = Students ,因为不支持反向设置多对一关系
    # 另外 ClassRoom.students 是一个方向查询对象 可以使用 .all() .filter() 等方法生成 Queryset


if __name__ == "__main__":
    run_async(run())
