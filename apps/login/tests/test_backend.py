# (c) Crown Owned Copyright, 2016. Dstl.
from django.test import TestCase
from apps.login.super_basic_auth_backend import SuperBasicAuth
from apps.users.models import User


class AuthBackendTest(TestCase):

    def test_user_doesnt_exist(self):
        auth = SuperBasicAuth()
        user = auth.authenticate(slug=1)

        self.assertIsNone(user)

    def test_user_exists(self):
        u1 = User(slug='user0001')
        u1.save()

        auth = SuperBasicAuth()
        user = auth.authenticate(slug=u1.slug)

        self.assertEquals(user, u1)
