# (c) Crown Owned Copyright, 2016. Dstl.
# apps/login/tests/test_login.py
from django.core.urlresolvers import reverse
from django_webtest import WebTest

from apps.users.models import User


class UserWebTest(WebTest):

    #   We want to test that a user who is missing a username is redirected
    #   to the update user profile page
    def test_user_missing_data_redirected(self):
        #   This user doesn't have a username
        u = User(slug='user0001')
        u.save()

        #   Let's log in as this user and see where we end up
        response = self.app.get(reverse('login-view'))
        response = response.click('user0001').follow()
        #   We should now be on the user needs to add information page
        self.assertEquals(
            response.html.find(
                'h1',
                attrs={'class': 'error-summary-heading'}
            ).text,
            'Please add a username'
        )

    #   Meanwhile a user who has a username will end up *not* on the
    #   udpate profile page (and even if they do it won't have any error
    #   alert waiting for them)
    def test_user_has_username_redirected(self):
        #   This user does have a username
        u = User(slug='user0001', username='User 0001')
        u.save()

        #   Let's log in as this user and see where we end up
        response = self.app.get(reverse('login-view'))
        response = response.click('user0001').follow()
        #   Make sure we *don't* have an error summary heading
        self.assertFalse(
            response.html.find(
                'h1',
                attrs={'class': 'error-summary-heading'}
            )
        )
