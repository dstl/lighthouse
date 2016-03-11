# (c) Crown Owned Copyright, 2016. Dstl.
# apps/users/tests.py
from django.core.urlresolvers import reverse
from django_webtest import WebTest


class UserWebTest(WebTest):

    def test_cannot_create_slugless_user(self):
        form = self.app.get(reverse('login-view')).form
        response = form.submit().follow().follow()
        login_label = response.html.find(
            'label',
            attrs={'class': 'form-label-bold', 'for': 'id_slug'}
        )
        self.assertTrue(login_label)
        self.assertEquals(login_label.text.strip(), 'Login with ID.')

    def test_create_new_user(self):
        #   got to the login form, and enter a user ID, this will sign us up.
        form = self.app.get(reverse('login-view')).form
        form['slug'] = 'user@0001.com'
        response = form.submit().follow()

        #   Now go to the user profile page
        response = self.app.get(
            reverse(
                'user-detail',
                kwargs={'slug': 'user0001com'}
            )
        )
        #   Check that we have the user slug in the name in the nav bar
        self.assertTrue(
            response.html.find(
                'span',
                attrs={'data-slug': 'user0001com'}
            )
        )
