# (c) Crown Owned Copyright, 2016. Dstl.

import re

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse

from django_webtest import WebTest

from apps.organisations.models import Organisation


class TeamWebTest(WebTest):
    def test_cannot_create_nameless_team(self):
        #   Create and log in a user
        get_user_model().objects.create_user(userid='user@0001.com')
        form = self.app.get(reverse('login')).form
        form['userid'] = 'user0001com'
        form.submit().follow()

        form = self.app.get(reverse('team-create')).form
        response = form.submit()
        form = response.context['form']
        self.assertIn(
            'This field is required.',
            form['name'].errors
        )

    def test_cannot_create_organisationless_team(self):
        #   Create and log in a user
        get_user_model().objects.create_user(userid='user@0001.com')
        form = self.app.get(reverse('login')).form
        form['userid'] = 'user0001com'
        form.submit().follow()

        form = self.app.get(reverse('team-create')).form
        form['name'] = 'New Team'
        response = form.submit()
        html = response.html
        errors = html.find(
            "ul",
            {"class": "form-error-list"}
        ).find("li").contents

        self.assertEqual(len(errors), 1)

        self.assertIn(
            'You must select an existing organisation or create a new one.',
            errors[0].text
        )

    def test_cannot_create_org_and_new_org_team(self):
        #   Create and log in a user
        get_user_model().objects.create_user(userid='user@0001.com')
        form = self.app.get(reverse('login')).form
        form['userid'] = 'user0001com'
        form.submit().follow()

        o = Organisation(name='New Org')
        o.save()
        form = self.app.get(reverse('team-create')).form
        form['name'] = 'New Team'
        form['organisation'] = str(o.pk)
        form['new_organisation'] = 'New Org'
        response = form.submit()
        html = response.html
        errors = html.find(
            "ul",
            {"class": "form-error-list"}
        ).find("li").contents

        self.assertEqual(len(errors), 1)

        failMessage = "You can't select an existing organisation and "
        failMessage += "create a new one at the same time."
        self.assertIn(failMessage, errors[0].text)

    def test_can_create_team_with_existsing_org(self):
        #   Create and log in a user
        get_user_model().objects.create_user(userid='user@0001.com')
        form = self.app.get(reverse('login')).form
        form['userid'] = 'user0001com'
        form.submit().follow()

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
        #   Create and log in a user
        get_user_model().objects.create_user(userid='user@0001.com')
        form = self.app.get(reverse('login')).form
        form['userid'] = 'user0001com'
        form.submit().follow()

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

    def test_can_create_team_from_list_view(self):
        #   Create and log in a user
        get_user_model().objects.create_user(userid='user@0001.com')
        form = self.app.get(reverse('login')).form
        form['userid'] = 'user0001com'
        form.submit().follow()

        org_name = 'New Org'
        team_name = 'New Team skippity bippity bop'
        form = self.app.get(reverse('team-list')).form
        form['name'] = team_name
        form['new_organisation'] = org_name
        response = form.submit()
        self.assertEquals(response.status_int, 302)

        #   Go get the list of teams so we can find the link of the team
        #   we just added (we know the team name but not the id)
        response = self.app.get(reverse('team-list'))
        response = self.app.get(response.html.find(
                'a',
                text=re.compile(team_name + r'')
            ).attrs['href']
        )
        org_name = response.html.find(
            'h1',
            attrs={'class': 'heading-xlarge'}
        ).get_text(strip=True)
        self.assertEquals(org_name, 'Team' + team_name)
