# -*- coding: utf-8 -*-
# @Time : 2021-04-05 07:33
# @Author : xzr
# @File : test_admin.py
# @Software: PyCharm
# @Contact : xzregg@gmail.com
# @Desc :
import json

from django.db import connection

from framework.route import reverse_view
from framework.tests import BaseTestCase
from framework.utils.log import logger
from myadmin.models import User
from . import LoginUserTestCase

class AdminTestCase(LoginUserTestCase):

    def tearDown(self):
        pass
        # for query in connection.queries:
        #     print(f"✅ {query['sql']}\n")

    def test_index_view(self):
        from ..views import index
        # response = self.client.get(reverse_view('myadmin.test.test_task'))
        request = self.factory.get(reverse_view('myadmin.index'))
        request.user = self.user
        response = index(request)
        self.assertEqual(response.status_code, 200)

    def test_userset_view(self):
        response = self.client.get(reverse_view('myadmin.user.list'), data=dict(format='json'))
        self.assertEqual(response.status_code, 200)

    def test_sayhello(self):
        from ..tasks import sayhello
        s = sayhello.delay(1, 2)

    def test_save(self):
        a = User()
        a.name = "'\;sd"
        # print(a.optimistic_save())
        b = User.objects.get(id=1)
        b = User.objects.get(id=1)
        b.password = '12323'
        b.last_ip = '1.1.1.1'
        # print(b.optimistic_save())
        # print(connection.queries)

        # print(connection.queries)
        # logger.error("testtest======")

    def test_password(self):
        from django.contrib.auth.password_validation import validate_password
        validate_password('123#232a32')

    def test_json(self):
        a = User()
        a.name = "'\;sd"
        print(a.optimistic_save())
        print(a.to_json())
        print(User.objects.all())
        from framework.utils import json_dumps

        query_set = User.objects.all()
        d = {"s": query_set, "b": "1"}
        jd = json_dumps(d)
        self.assertEqual(jd, json_dumps(json.loads(jd)))

    def test_autodiscover_app_view_functions(self):
        from myadmin.models.menu import MenuConfig
        app_menu_map = MenuConfig.autodiscover_app_view_functions()
        print(app_menu_map.keys())

    def test1_rest_docs(self):
        from drf_yasg.generators import OpenAPISchemaGenerator
        from rest_framework.schemas import SchemaGenerator
        from rest_framework import serializers
        from drf_yasg.errors import SwaggerGenerationError
        class TestSerializer(serializers.Serializer):
            email = serializers.EmailField()
            username = serializers.CharField(max_length=100)

        class UserSerializer1(serializers.ModelSerializer):

            class Meta:
                model = User

                exclude = ['role', 'session_key']

        class CommentSerializer(serializers.Serializer):
            user = TestSerializer()
            admin = UserSerializer1()
            content = serializers.CharField(max_length=200)
            created = serializers.DateTimeField()

        from drf_yasg import openapi
        from rest_framework.metadata import SimpleMetadata
        from drf_yasg.codecs import OpenAPICodecJson
        try:
            schema = OpenAPISchemaGenerator(openapi.Info(
                    title="Snippets API",
                    default_version='v1',
                    description="Test description",
                    terms_of_service="https://www.google.com/policies/terms/",
                    contact=openapi.Contact(email="contact@snippets.local"),
                    license=openapi.License(name="BSD License"),
            )).get_schema()
            codec = OpenAPICodecJson(validators=[], pretty=True)
            swagger_json = codec.encode(schema).decode('utf-8')
            #print(swagger_json)
            b = SimpleMetadata().get_serializer_info(CommentSerializer())
            #  print(b)
            schema_generator = SchemaGenerator(
            )
            schema = schema_generator.get_schema()
        except SwaggerGenerationError as e:
            pass
        # for k, v in schema.items():
        #     print(v.links)
        #     for name, link in v.links.items():
        #         print(link.fields)