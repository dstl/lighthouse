# (c) Crown Owned Copyright, 2016. Dstl.
# apps/users/tests.py
from django.core.urlresolvers import reverse
from django_webtest import WebTest
from django.test import TestCase
from django.db.utils import IntegrityError

from .models import User


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
        form = self.app.get(reverse('login-view')).form
        form['slug'] = 'user0001'
        response = form.submit().follow()
        self.assertEquals(response.status_int, 302)

        response = self.app.get(reverse('login-view'))
        response = response.click('user0001').follow()
        user_id = response.html.find_all(
                'span', attrs={'class': 'user_id'}
            )[0].text
        self.assertEquals(user_id, 'user0001')

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
