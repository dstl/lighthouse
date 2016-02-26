# apps/teams/tests.py
from django.core.urlresolvers import reverse
from django_webtest import WebTest
from django.test import TestCase
from django.db.utils import IntegrityError

from .models import Team
from apps.organisations.models import Organisation


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


class TeamWebTest(WebTest):
    def test_cannot_create_nameless_team(self):
        form = self.app.get(reverse('team-create')).form
        response = form.submit()
        form = response.context['form']
        self.assertIn(
            'This field is required.',
            form['name'].errors
        )

    def test_cannot_create_organisationless_team(self):
        form = self.app.get(reverse('team-create')).form
        form['name'] = 'New Team'
        response = form.submit()
        html = response.html
        errors = html.find("ul", {"class": "errorlist"}).find("li").contents
        self.assertIn(
            'You must select an existing organisation or create a new one.',
            errors
         )

    def test_cannot_create_org_and_new_org_team(self):
        o = Organisation(name='New Org')
        o.save()
        form = self.app.get(reverse('team-create')).form
        form['name'] = 'New Team'
        form['organisation'] = str(o.pk)
        form['new_organisation'] = 'New Org'
        response = form.submit()
        html = response.html
        errors = html.find("ul", {"class": "errorlist"}).find("li").contents
        failMessage = "You can't select an existing organisation and " + \
            "create a new one at the same time."
        self.assertIn(failMessage, errors)

    def test_can_create_team_with_existsing_org(self):
        o = Organisation(name='New Org')
        o.save()
        team_name = 'New Team skippity bippity bop'
        form = self.app.get(reverse('team-create')).form
        form['name'] = team_name
        form['organisation'] = str(o.pk)
        response = form.submit().follow()
        self.assertEquals(response.status_int, 200)
        html = response.html
        links = html.findAll("a", text=team_name)[0].contents
        self.assertIn(team_name, links)

    def test_can_create_team_with_new_org(self):
        org_name = 'New Org'
        team_name = 'New Team skippity bippity bop'
        form = self.app.get(reverse('team-create')).form
        form['name'] = team_name
        form['new_organisation'] = org_name
        response = form.submit().follow()
        self.assertEquals(response.status_int, 200)
        html = response.html
        links = html.findAll("a", text=team_name)[0].contents
        self.assertIn(team_name, links)
        #   But we also need to test that the organisation now exists in
        #   the db.
        check_org = Organisation.objects.filter(name=org_name).exists()
        self.assertTrue(check_org)
