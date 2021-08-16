from rest_framework import serializers

from ..response import RspData, RspError
from ..serializer import BaseModelSerializer
from ..translation import _
from ..utils import json_dumps
from . import BaseTestCase
import json

class TestFrameWork(BaseTestCase):

    def test_client_req(self):
        cleint = self.factory.request()

    def test_response(self):
        self.assertEqual(0, RspData(data={}, msg='asd').code)
        rsp = RspData()

        rsp.code = 1001
        print(rsp.code)
        print(rsp['code'])
        self.assertEqual(1001, rsp.code)
        self.assertEqual(rsp.code, 1001)
        err = RspError()
        print(err, err.code)
        print(json_dumps(rsp))
        print(rsp)

    def test_rsp_errenum(self):
        from ..response import RspErrorEnum, RspError

        class LoginErrors(RspErrorEnum):
            VERIFY_CODE_ERROR = RspError(_("验证码错误"), 111)
            LOGIN_TIMES_ERROR = RspError(_("登录次数过多"), 222)

        print(id(LoginErrors.LOGIN_TIMES_ERROR('ttt')), LoginErrors.LOGIN_TIMES_ERROR('ttt').msg,
              id(LoginErrors.LOGIN_TIMES_ERROR), LoginErrors.LOGIN_TIMES_ERROR)
        print(LoginErrors.member_list())

    def test_RspData(self):
        from ..response import RspData
        # @dataclass

        a = RspData(3, 54, 6)
        a.code
        print(a, a.code, a.msg)
        a.code = None
        a.msg = '123'
        print(a, a.code)
        self.assertEqual(a.code, None)
        print(json_dumps(a))

    def test_Serializer(self):
        class PageNumberPaginationSerializer(serializers.Serializer):
            count = serializers.IntegerField(label=_('总条目数'))
            next = serializers.URLField(label=_('下一页地址'), allow_null=True)
            previous = serializers.URLField(label=_('上一页地址'), allow_null=True)
            page = serializers.IntegerField(label=_('当前页数'))
            page_size = serializers.IntegerField(label=_('每页显示数量'))
            filter = serializers.DictField(label=_('查询条件'))

        from django.contrib.auth.models import User

        class AdminSerializer(BaseModelSerializer):
            # https://www.django-rest-framework.org/api-guide/serializers/
            # https://www.django-rest-framework.org/api-guide/relations/
            # role = serializers.PrimaryKeyRelatedField(many=True,label=_("拥有的角色"),queryset= Admin.role.field.related_model.objects.all() )

            class Meta:
                model = User
                fields = '__all__'

        class SubS(PageNumberPaginationSerializer, AdminSerializer): pass

        b = AdminSerializer()
        b.asd = 3
        print(b.asd)
        self.assertEqual(b.asd, 3)

    def test_setParamsSerializer(self):
        from ..serializer import ParamsSerializer, s
        from myadmin.models.user import User

        class AdminSerializer(BaseModelSerializer):
            f1 = s.CharField(label=_('f1'), default='default f1')
            f2 = s.CharField(label=_('f2'), default='default f1', allow_null=True, required=False)

            class Meta:
                model = User
                fields = '__all__'

        u = User()
        u.username = 'username'
        u.id = 3
        a = AdminSerializer(instance=u, data={'username': 'asd', 'alias': 'alias'}).o

        a.f1 = 'f1'
        a.username = 'c_username'
        self.assertEqual(a.f1, 'f1')
        self.assertTrue(a.get('f1'), 'f1')
        self.assertEqual(a.username, 'c_username')
        self.assertTrue(a.get('username'), 'c_username')

        class ChangePasswordSerializer(ParamsSerializer):
            old_password = s.CharField(label=_('旧密码'))
            new_password1 = s.CharField(label=_('新密码'), default='3')
            new_password2 = s.CharField(label=_('确认密码'))

        ss = ChangePasswordSerializer()
        ss.o.old_password = 'asd'
        ss.new_password2 = 'asd'
#        ss.validation()
        self.assertEqual(ss.data.old_password, 'asd')

        from framework.utils import json_dumps
        self.assertEqual(json_dumps(ss), json_dumps(json.loads(json_dumps(ss))))
