# (c) Crown Owned Copyright, 2016. Dstl.
from django.core.urlresolvers import reverse
from apps.links.models import Link
from apps.users.models import User

from django_webtest import WebTest


class LinkTest(WebTest):
    def test_create_link_not_logged_in(self):
        response = self.app.get(reverse('link-create')).follow()

        self.assertEqual(
            response.html.find('label', {"for": "id_slug"}).text.strip(' \n'),
            'Login with ID.'
        )

        self.assertIn('next=%s' % reverse('link-create'), response.request.url)

    def test_update_link_not_logged_in(self):
        a_user = User(
            slug='user0001',
            username='Fake Fakerly',
            phone='555-2187',
            email='fake@dstl.gov.uk')
        a_user.save()
        existing_link = Link(
            name='Wikimapia',
            description='A great mapping application',
            destination='https://wikimapia.org',
            owner=a_user)
        existing_link.save()

        response = self.app.get(
            reverse('link-edit', kwargs={'pk': existing_link.pk})).follow()

        self.assertEqual(
            response.html.find('label', {"for": "id_slug"}).text.strip(' \n'),
            'Login with ID.'
        )

        self.assertIn(
            'next=%s' % reverse('link-edit', kwargs={'pk': existing_link.pk}),
            response.request.url
        )
