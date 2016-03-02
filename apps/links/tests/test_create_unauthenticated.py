# (c) Crown Owned Copyright, 2016. Dstl.
from django.core.urlresolvers import reverse
from apps.links.models import Link
from .common import make_user

from django_webtest import WebTest


class LinkNotLoggedInTest(WebTest):
    def setUp(self):
        self.existing_user = make_user()
        self.existing_link = Link(
            name='Wikimapia',
            description='A great mapping application',
            destination='https://wikimapia.org',
            owner=self.existing_user)
        self.existing_link.save()

    def test_create_link_redirects_to_login(self):
        response = self.app.get(reverse('link-create')).follow()

        self.assertEqual(
            response.html.find('label', {"for": "id_slug"}).text.strip(' \n'),
            'Login with ID.'
        )

        self.assertIn('next=%s' % reverse('link-create'), response.request.url)

    def test_update_link_redirects_to_login(self):
        link_update_url = reverse(
            'link-edit',
            kwargs={'pk': self.existing_link.pk}
        )

        response = self.app.get(link_update_url).follow()

        self.assertEqual(
            response.html.find('label', {"for": "id_slug"}).text.strip(' \n'),
            'Login with ID.'
        )

        self.assertIn(
            'next=%s' % link_update_url,
            response.request.url
        )

    def test_update_link_follows_next(self):
        link_update_url = reverse(
            'link-edit',
            kwargs={'pk': self.existing_link.pk}
        )

        response = self.app.get(link_update_url).follow()

        user_login_url = reverse(
            'login-user',
            kwargs={'slug': self.existing_user.slug}
        )

        user_login_url += "?next=%s" % link_update_url

        user_login_link = response.html.find('a', {'href': user_login_url})

        self.assertIsNotNone(user_login_link)
        self.assertEqual(user_login_link.text, self.existing_user.slug)

        response = response.click(self.existing_user.slug).follow()

        self.assertIn(link_update_url, response.request.url)
        self.assertNotIn('next=%s' % link_update_url, response.request.url)
