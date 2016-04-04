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

    def test_user_can_have_multiple_teams_which_have_multiple_users(self):
        o = Organisation(name='New Org')
        o.save()

        t1 = Team(name='Team Awesome', organisation=o)
        t1.save()
        t2 = Team(name='Team Great', organisation=o)
        t2.save()

        u1 = get_user_model().objects.create_user(userid='teamplayer')
        u1.teams.add(t1)
        u1.teams.add(t2)
        u1.save()

        u2 = get_user_model().objects.create_user(userid='teamplayer2')
        u2.teams.add(t2)
        u2.save()

        self.assertIn(u1, t1.user_set.all())
        self.assertIn(u1, t2.user_set.all())
        self.assertNotIn(u2, t1.user_set.all())
        self.assertIn(u2, t2.user_set.all())

        self.assertEqual(len(t1.user_set.all()), 1)
        self.assertEqual(len(t2.user_set.all()), 2)
