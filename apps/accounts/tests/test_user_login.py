# (c) Crown Owned Copyright, 2016. Dstl.

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse

from django_webtest import WebTest


class UserWebTest(WebTest):
    def test_can_login(self):
        get_user_model().objects.create_user(userid='user@0001.com')

        form = self.app.get(reverse('login')).form
        form['userid'] = 'user@0001.com'
        response = form.submit().follow()

        # userid in the navigation, login link not
        self.assertTrue(
            response.html.find(
                'span',
                attrs={'data-slug': 'user0001com'}
            )
        )
        self.assertFalse(
            response.html.find('a', class_='login')
        )

    def test_new_userid_creates_normal_account(self):
        form = self.app.get(reverse('login')).form
        form['userid'] = 'user@0001.com'
        response = form.submit().follow()

        # userid in the navigation, login link not
        self.assertTrue(
            response.html.find(
                'span',
                attrs={'data-slug': 'user0001com'}
            )
        )
        self.assertFalse(
            response.html.find('a', class_='login')
        )

        # created a passwordless user in the db
        user = get_user_model().objects.get(slug='user0001com')
        self.assertTrue(user.pk)
        self.assertFalse(user.has_usable_password())

    def test_no_userid_doesnt_create_account(self):
        form = self.app.get(reverse('login')).form
        response = form.submit()

        # login link in the navigation
        self.assertTrue(
            response.html.find('a', class_='login')
        )

    def test_login_as_user_with_password_redirects_to_admin(self):
        get_user_model().objects.create_user(
            userid='user@0001.com', password='password')

        form = self.app.get(reverse('login')).form
        form['userid'] = 'user@0001.com'
        response = form.submit()
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.location, 'http://localhost:80/admin/')
