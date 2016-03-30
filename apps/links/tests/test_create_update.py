# (c) Crown Owned Copyright, 2016. Dstl.

from datetime import datetime
from unittest import mock

from django.core.urlresolvers import reverse
from django.utils.timezone import make_aware

from django_webtest import WebTest

from testing.common import make_user, login_user
from apps.links.models import Link


class LinkTest(WebTest):
    def setUp(self):
        self.logged_in_user = make_user()
        self.other_user = make_user(
            original_slug='other_user',
            email='fake2@dstl.gov.uk',
            name='Fake2 Fakerly')
        self.assertTrue(login_user(self, self.logged_in_user))

    def test_create_link(self):
        response = self.app.get(reverse('link-create'))
        form = response.form

        self.assertEquals(
            response.html.h1.get_text(strip=True), 'ToolAdd new tool'
        )

        self.assertEquals(form['name'].value, '')
        self.assertEquals(form['description'].value, '')
        self.assertEquals(form['destination'].value, '')
        self.assertEquals(form['categories'].value, '')

        form['name'] = 'Google'
        form['destination'] = 'https://google.com'
        response = form.submit().follow()
        self.assertIn('Google', response.html.find('h1').text)

        self.assertIn(
            'Fake Fakerly',
            response.html.find(id='link_owner').text,
        )

    def test_create_link_external(self):
        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = make_aware(datetime(2016, 3, 1, 10, 0, 0))

            form = self.app.get(reverse('link-create')).form

            self.assertEquals(form['name'].value, '')
            self.assertEquals(form['description'].value, '')
            self.assertEquals(form['destination'].value, '')
            self.assertEquals(form['categories'].value, '')
            self.assertEqual(form['is_external'].value, 'False')

            form['name'] = 'Google'
            form['destination'] = 'https://google.com'
            form['is_external'].select('True')
            response = form.submit().follow()
            self.assertIn('Google', response.html.find('h1').text)
            self.assertIn(
                'External',
                response.html.find(id="is_external").text
            )

            self.assertIn(
                '01/03/2016',
                response.html.find(id="date_added").text
            )

            self.assertIn(
                'Fake Fakerly',
                response.html.find(id='link_owner').text,
            )

    def test_update_link_button(self):
        existing_link = Link(
            name='Wikimapia',
            description='A great mapping application',
            destination='https://wikimapia.org',
            owner=self.logged_in_user,
            is_external=False)
        existing_link.save()

        response = self.app.get(
            reverse('link-detail', kwargs={'pk': existing_link.pk}))
        edit_button = response.html.find(None, {"id": "edit-button"})
        self.assertIsNotNone(edit_button)
        self.assertEqual(
            reverse('link-edit', kwargs={'pk': existing_link.pk}),
            edit_button.get('href')
        )

        self.assertTrue(login_user(self, self.other_user))

        response = self.app.get(
            reverse('link-detail', kwargs={'pk': existing_link.pk}))
        edit_button = response.html.find(None, {"id": "edit-button"})
        self.assertIsNone(edit_button)

    def test_update_link_external(self):
        existing_link = Link(
            name='Wikimapia',
            description='A great mapping application',
            destination='https://wikimapia.org',
            owner=self.logged_in_user,
            is_external=False)
        existing_link.save()

        response = self.app.get(
            reverse('link-edit', kwargs={'pk': existing_link.pk}))
        form = response.form

        self.assertEquals(response.html.h1.get_text(strip=True),
                          'ToolEdit %s' % existing_link.name)

        self.assertEquals(form['name'].value, 'Wikimapia')
        self.assertEquals(form['description'].value,
                          'A great mapping application')
        self.assertEquals(form['destination'].value, 'https://wikimapia.org')
        self.assertEqual(form['is_external'].value, 'False')

        form['is_external'].select('True')
        response = form.submit().follow()
        self.assertIn('Wikimapia', response.html.find('h1').text)
        self.assertIn('External', response.html.find(id="is_external").text)

    def test_create_empty_link(self):
        form = self.app.get(reverse('link-create')).form

        self.assertEquals(form['name'].value, '')
        self.assertEquals(form['description'].value, '')
        self.assertEquals(form['destination'].value, '')
        self.assertEquals(form['categories'].value, '')

        form['name'] = ''
        form['destination'] = ''
        response = form.submit()

        error_list = response.html.find('ul', {'class': 'form-error-list'})

        self.assertIsNotNone(error_list)
        self.assertEqual(len(error_list.findChildren('li')), 2)
        self.assertEqual(len(error_list.findChildren('a')), 2)

        self.assertIsNotNone(error_list.findChildren(
            'a', {"href": '#id_name_group'}
            ))
        self.assertIsNotNone(error_list.findChildren(
            'a', {"href": '#id_destination_group'}
            ))

        name_group = response.html.find(id='id_name_group')
        self.assertIsNotNone(name_group)

        name_errors = response.html.find(id='id_name_error_list')
        self.assertIsNotNone(name_errors)
        self.assertEqual(len(name_errors.findChildren()), 1)

        destination_errors = response.html.find(id='id_destination_error_list')
        self.assertIsNotNone(destination_errors)
        self.assertEqual(len(destination_errors.findChildren()), 1)

        form = response.form

        self.assertEquals(form['name'].value, '')
        self.assertEquals(form['description'].value, '')
        self.assertEquals(form['destination'].value, '')
        self.assertEquals(form['categories'].value, '')

    def test_edit_link_render(self):
        existing_link = Link(
            name='Wikimapia',
            description='A great mapping application',
            destination='https://wikimapia.org',
            owner=self.logged_in_user)
        existing_link.save()

        form = self.app.get(
            reverse('link-edit', kwargs={'pk': existing_link.pk})).form

        self.assertEquals(form['name'].value, 'Wikimapia')
        self.assertEquals(form['description'].value,
                          'A great mapping application')
        self.assertEquals(form['destination'].value, 'https://wikimapia.org')

    def test_edit_link_submit(self):
        existing_link = Link(
            name='Wikimapia',
            description='A great mapping application',
            destination='https://wikimapia.org',
            owner=self.logged_in_user)
        existing_link.save()

        form = self.app.get(
            reverse('link-edit', kwargs={'pk': existing_link.pk})).form

        self.assertEquals(form['name'].value, 'Wikimapia')
        self.assertEquals(form['description'].value,
                          'A great mapping application')
        self.assertEquals(form['destination'].value, 'https://wikimapia.org')

        form['name'].value = 'Bing Maps'
        form['description'].value = 'Another great mapping application'
        form['destination'].value = 'https://maps.bing.com'

        response = form.submit()

        self.assertEquals(
            'http://localhost:80%s' % reverse(
                'link-detail', kwargs={'pk': existing_link.pk}),
            response.location
        )

        response = response.follow()

        self.assertIn('Bing Maps', response)
        self.assertNotIn('Wikimapia', response)
        self.assertIn('Another great mapping application', response)
        self.assertNotIn('A great mapping application', response)
        self.assertIn('https://maps.bing.com', response)
        self.assertNotIn('https://wikimapia.org', response)

    def test_update_to_empty_link(self):
        existing_link = Link(
            name='Wikimapia',
            description='A great mapping application',
            destination='https://wikimapia.org',
            owner=self.logged_in_user)
        existing_link.save()

        form = self.app.get(
            reverse('link-edit', kwargs={'pk': existing_link.pk})).form

        self.assertEquals(form['name'].value, 'Wikimapia')
        self.assertEquals(form['description'].value,
                          'A great mapping application')
        self.assertEquals(form['destination'].value, 'https://wikimapia.org')

        form['name'].value = ''
        form['description'].value = 'Another great mapping application'
        form['destination'].value = 'https://maps.bing.com'

        response = form.submit()

        error_list = response.html.find('ul', {'class': 'form-error-list'})

        self.assertIsNotNone(error_list)
        self.assertEqual(len(error_list.findChildren('li')), 1)
        self.assertEqual(len(error_list.findChildren('a')), 1)

        self.assertIsNotNone(error_list.findChildren('a')[0].attrs['href'])
        self.assertEqual(
            error_list.findChildren('a')[0].attrs['href'],
            '#id_name_group'
        )

        name_group = response.html.find(id='id_name_group')
        self.assertIsNotNone(name_group)

        name_errors = response.html.find(id='id_name_error_list')
        self.assertIsNotNone(name_errors)
        self.assertEqual(len(name_errors.findChildren()), 1)

        form = response.form

        self.assertEquals(form['name'].value, '')
        self.assertEquals(form['description'].value,
                          'Another great mapping application')
        self.assertEquals(form['destination'].value, 'https://maps.bing.com')
        self.assertEquals(form['categories'].value, '')
