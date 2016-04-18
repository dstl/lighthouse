# (c) Crown Owned Copyright, 2016. Dstl.

from django.core.urlresolvers import reverse

from django_webtest import WebTest

from testing.common import make_user, login_user


class LighthouseGoToTest(WebTest):
    def test_lighthouse_page_has_no_goto_link(self):
        self.logged_in_user = make_user()
        self.app.get(reverse('login'))

        self.assertTrue(login_user(self, self.logged_in_user))

        response = self.app.get(reverse('link-detail', kwargs={'pk': 1}))

        goto_button = response.html.find(None, {'id': 'link_follow_button'})
        goto_url = response.html.find(None, {'id': 'link_follow_url'})

        self.assertIsNone(goto_button)
        self.assertIsNone(goto_url)

    def test_lighthouse_api_page_has_no_goto_link(self):
        self.logged_in_user = make_user()
        self.app.get(reverse('login'))

        self.assertTrue(login_user(self, self.logged_in_user))

        response = self.app.get(reverse('link-detail', kwargs={'pk': 2}))

        goto_button = response.html.find(None, {'id': 'link_follow_button'})
        goto_url = response.html.find(None, {'id': 'link_follow_url'})

        self.assertIsNone(goto_button)
        self.assertIsNone(goto_url)
