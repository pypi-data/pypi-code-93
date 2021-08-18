"""
@Author: WangYuXiang
@E-mile: Hill@3io.cc
@CreateTime: 2021/3/15 19:05
@DependencyLibrary: 无
@MainFunction：无
@FileDoc:
    test_o2o.py
    一对一模型
@ChangeHistory:
    datetime action why
    example:
    2021/2/4 14:35 change 'Fix bug'

"""

from tortoise import Model, Tortoise, run_async
from tortoise import fields


class User(Model):
    account = fields.CharField(12)
    password = fields.CharField(128)


class Students(Model):
    name = fields.CharField(30)
    user: fields.OneToOneRelation[User] = fields.OneToOneField('models.User', 'student', null=True)


async def run():
    await Tortoise.init(db_url="sqlite://./db.sqlite", modules={"models": ["__main__"]})
    await Tortoise.generate_schemas()

    # 测试正向创建
    user = User(account='17674707037', password='123456')
    await user.save()
    std = Students(name='刘桂香', user=user)
    await std.save()
    print(type(user.student))
    c = await user.student
    print(await user.student)
    print(await user.student.model)

    # 测试逆向创建
    std = Students(name='刘桂香')
    user = User(account='17674707037', password='123456')
    std.user = user
    await std.save()
    await user.save()
    # 结论 一对一只能由单边发起
    # 列如在 Students 类中设置了一对一关系，那么必须先创建对应的 User 然后才能创建 Students
    # 在 Students.user 允许为空的情况下，可以先创建 Students 再创建 User
    # 先创建 Students 再创建 User ,如果需要关联一对一那么只能 Students.user=User,
    # 不可以 User.student = Students ,因为不支持反向设置一对一关系


if __name__ == "__main__":
    run_async(run())
