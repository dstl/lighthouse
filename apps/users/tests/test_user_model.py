# (c) Crown Owned Copyright, 2016. Dstl.
from django.test import TestCase
from django.db.utils import IntegrityError

from apps.users.models import User
from apps.teams.models import Team
from apps.organisations.models import Organisation


class UserTest(TestCase):
    def setUp(self):
        u = User(slug='user0001com', original_slug='user@0001.com')
        u.save()

    def test_can_create_user(self):
        u = User(slug='user0002com', original_slug='user@0002.com')
        u.save()
        self.assertTrue(u.slug)

    def test_cannot_create_duplicate_user(self):
        u = User(slug='user0002com', original_slug='user@0002.com')
        u.save()
        self.assertTrue(u.slug)
        u = User(slug='user0001com', original_slug='user@0001.com')
        with self.assertRaises(IntegrityError):
            u.save()

    def test_user_can_have_multiple_teams_which_have_multiple_users(self):
        o = Organisation(name='New Org')
        o.save()

        t1 = Team(name='Team Awesome', organisation=o)
        t1.save()
        t2 = Team(name='Team Great', organisation=o)
        t2.save()

        u1 = User(slug='teamplayer')
        u1.save()

        u1.teams.add(t1)
        u1.teams.add(t2)
        u1.save()

        u2 = User(slug='teamplayer2')
        u2.save()

        u2.teams.add(t2)
        u2.save()

        self.assertIn(u1, t1.user_set.all())
        self.assertIn(u1, t2.user_set.all())
        self.assertNotIn(u2, t1.user_set.all())
        self.assertIn(u2, t2.user_set.all())

        self.assertEqual(len(t1.user_set.all()), 1)
        self.assertEqual(len(t2.user_set.all()), 2)
