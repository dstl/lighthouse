# (c) Crown Owned Copyright, 2016. Dstl.

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.organisations.models import Organisation
from apps.teams.models import Team


class UserModelTest(TestCase):
    def test_can_create_user_without_password(self):
        user = get_user_model().objects.create_user(userid='user@0001.com')
        self.assertTrue(user.pk)
        self.assertEqual(user.slug, 'user0001com')
        self.assertFalse(user.has_usable_password())

    def test_can_create_user_with_password(self):
        user = get_user_model().objects.create_user(
            userid='user@0001.com', password='password')
        self.assertTrue(user.pk)
        self.assertEqual(user.slug, 'user0001com')
        self.assertTrue(user.has_usable_password())

    def test_create_user_with_unique_slugs(self):
        user = get_user_model().objects.create_user(userid='user@0001.com')
        self.assertTrue(user.pk)
        self.assertEqual(user.slug, 'user0001com')
        user = get_user_model().objects.create_user(userid='us.er@0001.com')
        self.assertTrue(user.pk)
        self.assertEqual(user.slug, 'user0001com1')
        user = get_user_model().objects.create_user(userid='u.s.e.r@0001.com')
        self.assertTrue(user.pk)
        self.assertEqual(user.slug, 'user0001com2')
