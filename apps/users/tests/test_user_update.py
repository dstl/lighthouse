# (c) Crown Owned Copyright, 2016. Dstl.
# apps/users/tests.py
from django.core.urlresolvers import reverse
from django_webtest import WebTest

from apps.users.models import User
from apps.teams.models import Team
from apps.organisations.models import Organisation

import re


class UserWebTest(WebTest):
    def test_update_button_shows_on_user_profile(self):
        #   Create the two users
        u1 = User(slug='user0001com', original_slug='user@0001.com')
        u1.save()
        u2 = User(slug='user0002com', original_slug='user@0002.com')
        u2.save()
        #   Login as the first user
        form = self.app.get(reverse('login-view')).form
        form['slug'] = 'user0001com'
        response = form.submit()

        #   Now goto the profile page for the 1st user and see if the button
        #   exists
        response = self.app.get(reverse(
            'user-detail',
            kwargs={'slug': 'user0001com'}))
        button = response.html.find(
                'a',
                attrs={'id': 'update_profile_link'})
        self.assertTrue(button)

        #   Now visit the profile page for the not logged in user
        response = self.app.get(reverse(
            'user-detail',
            kwargs={'slug': 'user0002com'}))
        button = response.html.find(
                'a',
                attrs={'id': 'update_profile_link'})
        self.assertFalse(button)

    #   Test that a user can join an existing team when editing their
    #   own profile
    def test_adding_new_existing_team(self):
        u = User(slug='user0001com', original_slug='user@0001.com')
        u.save()
        o = Organisation(name='org0001')
        o.save()
        t = Team(name='team0001', organisation=o)
        t.save()

        #   Log in as user
        form = self.app.get(reverse('login-view')).form
        form['slug'] = 'user0001com'
        form.submit()

        #   Go to the user's profile page and assert that the team is NOT
        #   showing up in the list of teams they are a member of.
        response = self.app.get(reverse(
            'user-detail',
            kwargs={'slug': 'user0001com'}))
        self.assertFalse(response.html.find('a', text=re.compile(r'team0001')))

        #   Now go to the update profile page and check the first team
        #   in the list of teams.
        form = self.app.get(reverse(
            'user-update-teams',
            kwargs={'slug': 'user0001com'})).form
        form.get('team', index=0).checked = True
        form.submit()

        #   Go back to the users profile page to see if the team is now
        #   on the list of teams
        response = self.app.get(reverse(
            'user-detail',
            kwargs={'slug': 'user0001com'}))
        self.assertTrue(response.html.find('a', text=re.compile(r'team0001')))

    #   Test that the user can join a new team connecting it to an existsing
    #   organisation
    def test_adding_new_team_existing_organisation(self):
        u = User(slug='user0001com', original_slug='user@0001.com')
        u.save()
        o = Organisation(name='org0001')
        o.save()

        #   Log in as user
        form = self.app.get(reverse('login-view')).form
        form['slug'] = 'user0001com'
        form.submit()

        #   Now go to the update profile page and check the first team
        #   in the list of teams.
        form = self.app.get(reverse(
            'user-update-teams',
            kwargs={'slug': 'user0001com'})).form
        form['name'] = 'team0001'
        form['organisation'].value = o.pk
        form.submit()

        #   Go back to the users profile page to see if the team is now
        #   on the list of teams
        response = self.app.get(reverse(
            'user-detail',
            kwargs={'slug': 'user0001com'}))
        self.assertTrue(response.html.find('a', text=re.compile(r'team0001')))

    #   Test that the user can join a new team connecting it to an existsing
    #   organisation
    def test_adding_new_team_new_organisation(self):
        u = User(slug='user0001com', original_slug='user@0001.com')
        u.save()

        #   Log in as user
        form = self.app.get(reverse('login-view')).form
        form['slug'] = 'user0001com'
        form.submit()

        #   Now go to the update profile "teams" page and add a new team
        form = self.app.get(reverse(
            'user-update-teams',
            kwargs={'slug': 'user0001com'})).form
        form['name'] = 'team0001'
        form['new_organisation'] = 'org0001'
        form.submit()

        #   Go back to the users profile page to see if the team and
        #   organisation is now on the list of teams
        response = self.app.get(reverse(
            'user-detail',
            kwargs={'slug': 'user0001com'}))
        self.assertTrue(response.html.find('a', text=re.compile(r'team0001')))
        self.assertTrue(response.html.find('a', text=re.compile(r'org0001')))

    def test_alert_for_missing_username(self):
        #   This user doesn't have a username
        User(slug='user0001com', original_slug='user@0001.com').save()

        #   Log in as user
        form = self.app.get(reverse('login-view')).form
        form['slug'] = 'user0001com'
        response = form.submit()

        #   Now go to the update user information page for this user-detail
        response = self.app.get(reverse(
            'user-updateprofile',
            kwargs={'slug': 'user0001com'}))

        #   Check that we have an error summary at the top
        self.assertTrue(
            response.html.find(
                'h3',
                attrs={'class': 'error-summary-heading'}
            )
        )

    def test_alert_for_missing_other_information(self):

        update_page = reverse(
            'user-updateprofile',
            kwargs={'slug': 'user0001com'})
        check_str = 'Please add additional information'

        def find_alert(response):
            return response.html.find(
                        'h3',
                        attrs={'class': 'alert-summary-heading'}
                        )

        #   create the user and log them in
        u = User(
            slug='user0001com',
            original_slug='user@0001.com',
            username='User 0001'
        )
        u.save()
        form = self.app.get(reverse('login-view')).form
        form['slug'] = 'user0001com'
        response = form.submit()

        # go to the update page and check for the alert
        response = self.app.get(update_page)
        self.assertTrue(find_alert(response), check_str)

        u.best_way_to_find = 'In the kitchen'
        u.best_way_to_contact = 'By phone'
        u.phone = '01777777'
        u.email = ''
        u.save()
        #   Check that we have an alert summary at the top
        response = self.app.get(update_page)
        self.assertTrue(find_alert(response), check_str)

        u.best_way_to_find = 'In the kitchen'
        u.best_way_to_contact = 'By phone'
        u.phone = ''
        u.email = 'test@test.com'
        u.save()
        #   Check that we have an alert summary at the top
        response = self.app.get(update_page)
        self.assertTrue(find_alert(response), check_str)

        u.best_way_to_find = 'In the kitchen'
        u.best_way_to_contact = ''
        u.phone = '01777777'
        u.email = 'test@test.com'
        u.save()
        #   Check that we have an alert summary at the top
        response = self.app.get(update_page)
        self.assertTrue(find_alert(response), check_str)

        u.best_way_to_find = ''
        u.best_way_to_contact = 'By phone'
        u.phone = '01777777'
        u.email = 'test@test.com'
        u.save()
        #   Check that we have an alert summary at the top
        response = self.app.get(update_page)
        self.assertTrue(find_alert(response), check_str)

    def test_no_error_alert_for_all_information(self):
        #   This user has all the information
        User(
            slug='user0001com',
            original_slug='user@0001.com',
            username='User 0001',
            best_way_to_find='In the kitchen',
            best_way_to_contact='By phone',
            phone='01777777',
            email='test@test.com',
        ).save()

        #   Log in as user
        form = self.app.get(reverse('login-view')).form
        form['slug'] = 'user0001com'
        response = form.submit()

        #   Now go to the update user information page for this user-detail
        response = self.app.get(reverse(
            'user-updateprofile',
            kwargs={'slug': 'user0001com'}))

        #   Check that we don't have an error or alert summary
        self.assertFalse(
            response.html.find(
                'h1',
                attrs={'class': 'error-summary-heading'}
            )
        )

        self.assertFalse(
            response.html.find(
                'h1',
                attrs={'class': 'alert-summary-heading'}
            )
        )
