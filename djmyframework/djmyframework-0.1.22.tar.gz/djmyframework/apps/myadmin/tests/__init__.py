# Create your tests here.
import json

from django.db import connection


from framework.route import reverse_view
from framework.tests import BaseTestCase
from framework.utils.log import logger
from myadmin.models import User


class LoginUserTestCase(BaseTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.create_root()

    def setUp(self):
        super().setUp()
        self.client.real_ip = '127.0.0.1'
        self.client.META = {}
        User.login_user(self.client, self.user)
        self.client._login(self.user)


