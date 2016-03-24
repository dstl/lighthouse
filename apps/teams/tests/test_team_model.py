# (c) Crown Owned Copyright, 2016. Dstl.

from django.db.utils import IntegrityError
from django.test import TestCase

from apps.organisations.models import Organisation
from apps.teams.models import Team


class TeamTest(TestCase):
    def setUp(self):
        o = Organisation(name='Existing Org')
        o.save()
        t = Team(name='Existing Team', organisation=o)
        t.save()

    def test_cannot_add_team_without_organisation(self):
        t = Team(name='New Team')
        self.assertIsNone(t.pk)

    #   Wut???? TODO: De-Wutify this...
    #   How do we test for ValueError?
    """
    def test_cannot_add_team_with_not_organisation(self):
        o = Organisation(name='New Org')
        o.save()
        t1 = Team(name='New Team 1', organisation=o)
        t1.save()
        t2 = Team(name='New Team 2', organisation=t1)
        self.assertRaises(ValueError, t2.save())
    """

    def test_cannot_create_duplicate_team(self):
        t = Team(name='Existing Team')
        with self.assertRaises(IntegrityError):
            t.save()

    def test_can_create_team(self):
        o = Organisation(name='New Org')
        o.save()
        self.assertTrue(o.pk)
        t = Team(name='New Team', organisation=o)
        t.save()
        self.assertTrue(t.pk)
