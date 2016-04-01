# (c) Crown Owned Copyright, 2016. Dstl.

import re

from django.core.urlresolvers import reverse

from django_webtest import WebTest

from testing.common import create_organisation
from apps.organisations.models import Organisation
from apps.users.models import User


class OrganisationListWebTest(WebTest):
    def test_can_click_through_existing_organisation_link(self):
        #   Create and log in a user
        User(slug='user0001com', original_slug='user@0001.com').save()
        form = self.app.get(reverse('login-view')).form
        form['slug'] = 'user0001com'
        form.submit().follow()

        o = Organisation(name='org0001')
        o.save()
        response = self.app.get(reverse('organisation-list'))
        response = self.app.get(response.html.find(
                'a',
                text=re.compile(o.name + r'')
            ).attrs['href']
        )
        org_name = response.html.find(
            'h1',
            attrs={'class': 'heading-xlarge'}
        ).get_text(strip=True)
        self.assertEquals(org_name, 'Organisation' + o.name)

    def test_show_number_of_teams_two(self):
        #   Create and log in a user
        User(slug='user0001com', original_slug='user@0001.com').save()
        form = self.app.get(reverse('login-view')).form
        form['slug'] = 'user0001com'
        form.submit().follow()

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
        #   Create and log in a user
        User(slug='user0001com', original_slug='user@0001.com').save()
        form = self.app.get(reverse('login-view')).form
        form['slug'] = 'user0001com'
        form.submit().follow()

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
