# (c) Crown Owned Copyright, 2016. Dstl.

from django.core.urlresolvers import reverse

from django_webtest import WebTest

from apps.links.models import Link
from apps.organisations.models import Organisation
from apps.teams.models import Team
from testing.common import make_user


class LinkNotLoggedInTest(WebTest):
    def setUp(self):
        self.complete_user = make_user()
        self.complete_user.best_way_to_find = 'Whatever'
        self.complete_user.best_way_to_contact = 'Whatever'
        o = Organisation.objects.create(name='Whatever')
        t = Team.objects.create(name='Whatever', organisation=o)
        self.complete_user.teams.add(t)
        self.complete_user.save()

        self.incomplete_user = make_user(
            original_slug='user@0002.com',
            email='fake2@dstl.gov.uk',
            name='Fake2 Fakerly')
        self.incomplete_user.teams.add(t)
        self.incomplete_user.save()

        self.teamless_user = make_user(
            original_slug='user@0003.com',
            email='fake3@dstl.gov.uk',
            name='Fake3 Fakerly')
        self.teamless_user.best_way_to_find = 'Whatever'
        self.teamless_user.best_way_to_contact = 'Whatever'
        self.teamless_user.save()

        self.existing_link = Link(
            name='Wikimapia',
            description='A great mapping application',
            destination='https://wikimapia.org',
            owner=self.complete_user)

        self.existing_link.save()

    def test_create_link_redirects_to_login(self):
        response = self.app.get(reverse('link-create')).follow()

        self.assertEqual(
            response.html.find('label', {"for": "id_slug"}).text.strip(' \n'),
            'Login with ID.'
        )

        self.assertIn('next=%s' % reverse('link-create'), response.request.url)
        return response

    def test_login_but_follows_when_logged_in_for_completed_user(self):
        response = self.test_create_link_redirects_to_login()

        form = response.form
        form['slug'] = self.complete_user.slug
        response = form.submit().follow()

        self.assertNotIn(
            'next=%s' % reverse('link-create'),
            response.request.url
        )
        self.assertIn(reverse('link-create'), response.request.url)

    def test_login_but_follows_when_logged_in_for_incomplete_user(self):
        response = self.test_create_link_redirects_to_login()

        form = response.form
        form['slug'] = self.incomplete_user.slug
        response = form.submit().follow()

        self.assertNotIn(
            'next=%s' % reverse('link-create'),
            response.request.url
        )
        self.assertIn(reverse('link-create'), response.request.url)

    def test_login_but_follows_when_logged_in_for_teamless_user(self):
        response = self.test_create_link_redirects_to_login()

        form = response.form
        form['slug'] = self.teamless_user.slug
        response = form.submit().follow()

        self.assertNotIn(
            'next=%s' % reverse('link-create'),
            response.request.url
        )
        self.assertIn(reverse('link-create'), response.request.url)

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
