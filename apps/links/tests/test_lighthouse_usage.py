# (c) Crown Owned Copyright, 2016. Dstl.

from django.core.urlresolvers import reverse
from django.test import LiveServerTestCase

from django_webtest import WebTest
import requests

from apps.links.models import Link, LinkUsage
from testing.common import make_user, login_user


class LighthouseUsageTest(WebTest):
    def test_every_authenticated_page_hit_generates_usage(self):
        self.logged_in_user = make_user()

        # This should not create usage, since they aren't logged in
        self.app.get(reverse('login'))

        # Three usages here
        self.assertTrue(login_user(self, self.logged_in_user))
        self.app.get(reverse('user-list'))
        self.app.get(reverse('link-list'))

        lighthouse_link = Link.objects.get(pk=1)
        self.assertEqual(lighthouse_link.name, 'Lighthouse')

        all_usage = LinkUsage.objects.all()

        self.assertEqual(len(all_usage), 1)

        self.assertEqual(all_usage[0].link, lighthouse_link)
        self.assertEqual(all_usage[0].user, self.logged_in_user)


class LighthouseApiUsageTest(LiveServerTestCase):
    def test_api_posts_generate_usage(self):
        user = make_user()
        link = Link.objects.create(
            name='Link Linkerly',
            destination='link.com',
            owner=user,
            is_external=False,
        )

        link_api_url = '%s%s' % (
            self.live_server_url,
            reverse('api-link-usage', kwargs={'pk': link.pk}),
        )
        requests.post(link_api_url, data={'user': user.slug})

        self.assertEquals(link.usage_total(), 1)

        api = Link.objects.get(pk=2)
        self.assertEquals(api.usage_total(), 1)
