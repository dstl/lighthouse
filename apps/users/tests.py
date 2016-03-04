# (c) Crown Owned Copyright, 2016. Dstl.
# apps/users/tests.py
from django.core.urlresolvers import reverse
from django_webtest import WebTest
from django.test import TestCase
from django.db.utils import IntegrityError

from .models import User
from apps.teams.models import Team
from apps.organisations.models import Organisation


class UserTest(TestCase):
    def setUp(self):
        u = User(slug='user0001')
        u.save()

    def test_can_create_user(self):
        u = User(slug='user0002')
        u.save()
        self.assertTrue(u.slug)

    def test_cannot_create_duplicate_user(self):
        u = User(slug='user0002')
        u.save()
        self.assertTrue(u.slug)
        u = User(slug='user0001')
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


class UserWebTest(WebTest):

    def test_cannot_create_nameless_user(self):
        form = self.app.get(reverse('login-view')).form
        response = form.submit()
        form = response.context['form']
        self.assertIn(
            'This field is required.',
            form['slug'].errors
        )

    def test_create_new_user(self):
        #   got to the login form, and enter a user ID, this will sign us up.
        form = self.app.get(reverse('login-view')).form
        form['slug'] = 'user0001'
        response = form.submit().follow()

        #   Now go to the user profile page
        response = self.app.get(
            reverse(
                'user-detail',
                kwargs={'slug': 'user0001'}
            )
        )
        #   Check that we have the user slug in the name in the nav bar
        self.assertTrue(
            response.html.find(
                'span',
                attrs={'data-slug': 'user0001'}
            )
        )

    def test_cannot_create_duplicate_user(self):
        u = User(slug='user0001')
        u.save()
        form = self.app.get(reverse('login-view')).form
        form['slug'] = 'user0001'
        response = form.submit()
        form = response.context['form']
        self.assertIn(
            'User with this Slug already exists.',
            form['slug'].errors
        )

    def test_can_login_as_existing_user_via_link(self):
        #   Pop a user into the database
        self.user = User(
            slug='user0001'
        )
        self.user.save()

        #   Now visit the login page, find the user in the list, click
        #   it then check for the username/slug in the navgiation of
        #   the next page.
        response = self.app.get(reverse('login-view'))
        response = response.click('user0001').follow()
        user_id = response.html.find_all(
                'span', attrs={'class': 'user_id'}
            )[0].text
        self.assertEquals(user_id, 'user0001')

    def test_update_button_shows_on_user_profile(self):
        #   Create the two users
        u1 = User(slug='user0001')
        u1.save()
        u2 = User(slug='user0002')
        u2.save()
        #   Login as the first user
        response = self.app.get(reverse('login-view'))
        response = response.click('user0001').follow()
        #   Now goto the profile page for the 1st user and see if the button
        #   exists
        response = self.app.get(reverse(
            'user-detail',
            kwargs={'slug': 'user0001'}))
        button = response.html.find(
                'a',
                attrs={'id': 'update_profile_link'})
        self.assertTrue(button)

        #   Now visit the profile page for the not logged in user
        response = self.app.get(reverse(
            'user-detail',
            kwargs={'slug': 'user0002'}))
        button = response.html.find(
                'a',
                attrs={'id': 'update_profile_link'})
        self.assertFalse(button)

    def test_alert_for_missing_username(self):
        #   This user doesn't have a username
        User(slug='user0001').save()

        #   Log in as them
        response = self.app.get(reverse('login-view'))
        response = response.click('user0001')

        #   Now go to the update user information page for this user-detail
        response = self.app.get(reverse(
            'user-updateprofile',
            kwargs={'slug': 'user0001'}))

        #   Check that we have an error summary at the top
        self.assertTrue(
            response.html.find(
                'h1',
                attrs={'class': 'error-summary-heading'}
            )
        )

    def test_alert_for_missing_other_information(self):

        update_page = reverse(
            'user-updateprofile',
            kwargs={'slug': 'user0001'})
        check_str = 'Please add additional information'

        def find_alert(response):
            return response.html.find(
                        'h1',
                        attrs={'class': 'alert-summary-heading'}
                        )

        #   create the user and log them in
        u = User(slug='user0001', username='User 0001')
        u.save()
        response = self.app.get(reverse('login-view'))
        response = response.click('user0001')

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
            slug='user0001',
            username='User 0001',
            best_way_to_find='In the kitchen',
            best_way_to_contact='By phone',
            phone='01777777',
            email='test@test.com',
        ).save()

        #   Log in as them
        response = self.app.get(reverse('login-view'))
        response = response.click('user0001')

        #   Now go to the update user information page for this user-detail
        response = self.app.get(reverse(
            'user-updateprofile',
            kwargs={'slug': 'user0001'}))

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
