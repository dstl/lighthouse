from django.test import TestCase
from apps.login.super_basic_auth_backend import SuperBasicAuth
from apps.users.models import User


class AuthBackendTest(TestCase):

    def test_user_doesnt_exist(self):
        auth = SuperBasicAuth()
        user = auth.authenticate(user_id=1)

        self.assertIsNone(user)

    def test_user_exists(self):
        u1 = User(fullName='Jane Smith')
        u1.save()

        auth = SuperBasicAuth()
        user = auth.authenticate(user_id=1)

        self.assertEquals(user, u1)
