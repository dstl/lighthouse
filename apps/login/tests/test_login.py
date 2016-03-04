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

        #   Log in as user
        form = self.app.get(reverse('login-view')).form
        form['slug'] = 'user0001'
        response = form.submit().follow()

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

        #   Log in as user
        form = self.app.get(reverse('login-view')).form
        form['slug'] = 'user0001'
        response = form.submit().follow()

        #   Make sure we *don't* have an error summary heading
        self.assertFalse(
            response.html.find(
                'h1',
                attrs={'class': 'error-summary-heading'}
            )
        )

    #   Check that a link showing the user's slug appears in the top nav
    #   bar
    def test_slug_and_link_exists_in_nav(self):
        #   Create the user
        User(slug='user0001').save()

        #   Log in as user
        form = self.app.get(reverse('login-view')).form
        form['slug'] = 'user0001'
        response = form.submit()

        #   Go to the profile page (any page would do)
        response = self.app.get(
            reverse(
                'user-detail',
                kwargs={'slug': 'user0001'}
            )
        )

        #   Check that the slug is displayed at the top, that it has a link
        #   and the link test is the user's slug
        slug_div = response.html.find(
                    'span',
                    attrs={'data-slug': 'user0001'}
                )
        self.assertTrue(slug_div)
        slug_link = slug_div.find('a')
        self.assertTrue(slug_link)
        slug_text = slug_link.text
        self.assertEquals(slug_text, 'user0001')

    #   Check that a link showing the user's username appears in the top nav
    #   bar
    def test_username_and_link_exists_in_nav(self):
        #   Create the user
        User(slug='user0001', username='User 0001').save()

        #   Log in as user
        form = self.app.get(reverse('login-view')).form
        form['slug'] = 'user0001'
        response = form.submit()

        #   Go to the profile page (any page would do)
        response = self.app.get(
            reverse(
                'user-detail',
                kwargs={'slug': 'user0001'}
            )
        )

        #   Check that the username is displayed at the top, that it has a link
        #   and the link test is the user's slug
        slug_div = response.html.find(
                    'span',
                    attrs={'data-slug': 'user0001'}
                )
        self.assertTrue(slug_div)
        slug_link = slug_div.find('a')
        self.assertTrue(slug_link)
        slug_text = slug_link.text
        self.assertEquals(slug_text, 'User 0001')
