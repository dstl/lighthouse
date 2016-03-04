# (c) Crown Owned Copyright, 2016. Dstl.
# apps/organisations/tests.py
from django.core.urlresolvers import reverse
from django_webtest import WebTest
from django.test import TestCase
from django.db.utils import IntegrityError

from .models import Organisation
from apps.teams.models import Team


def create_organisation(name, num_teams=0):
    o = Organisation(name=name)
    o.save()
    for x in range(0, num_teams):
        Team(name='New Team %d' % (x + 1), organisation=o).save()
    return o


class OrganisationTest(TestCase):
    def setUp(self):
        o = Organisation(name='Existing Org')
        o.save()

    def test_cannot_add_nameless_organisation(self):
        # FIXME write the damn test
        pass

    def test_can_create_organisation(self):
        o = Organisation(name='testy')
        o.save()
        self.assertTrue(o.pk)

    def test_cannot_create_duplicate_organisations(self):
        o = Organisation(name='New Org')
        o.save()
        self.assertTrue(o.pk)
        o = Organisation(name='Existing Org')
        with self.assertRaises(IntegrityError):
            o.save()


class OrganisationWebTest(WebTest):

    def test_cannot_create_nameless_organisation(self):
        form = self.app.get(reverse('organisation-create')).form
        response = form.submit()
        form = response.context['form']
        self.assertIn(
            'This field is required.',
            form['name'].errors
        )

    def test_create_new_organisation_from_list_view(self):
        form = self.app.get(reverse('organisation-list')).form
        form['name'] = 'alpha'
        response = form.submit()
        self.assertEquals(response.status_int, 302)

        response = self.app.get(reverse('organisation-list'))
        response = response.click('alpha')
        org_name = response.html.find(
            'h1',
            attrs={'class': 'heading-xlarge'}
        ).text
        self.assertEquals(org_name, 'Organisation: alpha')

    def test_cannot_create_duplicate_organisation(self):
        o = Organisation(name='alpha')
        o.save()
        form = self.app.get(reverse('organisation-list')).form
        form['name'] = 'alpha'
        response = form.submit()
        form = response.context['form']
        self.assertIn(
            'Organisation with this Name already exists.',
            form['name'].errors
        )

    def test_can_click_through_existing_organisation_link(self):
        o = Organisation(name='alpha')
        o.save()
        response = self.app.get(reverse('organisation-list'))
        response = response.click('alpha')
        org_name = response.html.find(
            'h1',
            attrs={'class': 'heading-xlarge'}
        ).text
        self.assertEquals(org_name, 'Organisation: alpha')

    def test_show_number_of_teams_two(self):
        o = create_organisation(name='two teams', num_teams=2)
        response = self.app.get(reverse('organisation-list'))

        self.assertIn(
            o.name,
            response.html.find('a', {"class": "main-list-item"}).text
        )
        self.assertIn(
            'Total teams: 2',
            response.html.find('ul', {"class": "organisation-info"}).text
        )

    def test_show_number_of_teams_none(self):
        o = create_organisation(name='no teams', num_teams=0)
        response = self.app.get(reverse('organisation-list'))

        self.assertIn(
            o.name,
            response.html.find('a', {"class": "main-list-item"}).text
        )
        self.assertIn(
            'This organisation has no teams',
            response.html.find('ul', {"class": "organisation-info"}).text
        )
