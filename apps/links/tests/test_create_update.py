from django.core.urlresolvers import reverse
from apps.links.models import Link
from apps.users.models import User

from django_webtest import WebTest


class LinkTest(WebTest):
    def setUp(self):
        self.logged_in_user = User(
            fullName='Fake Fakerly',
            phone='555-2187',
            email='fake@dstl.gov.uk')
        self.logged_in_user.save()

        response = self.app.get(reverse('login-view'))

        response = response.click('Fake Fakerly').follow()

        self.assertEquals(response.html.h1.text, 'Fake Fakerly')

    def test_create_link(self):
        form = self.app.get(reverse('link-create')).form

        self.assertEquals(form['name'].value, '')
        self.assertEquals(form['description'].value, '')
        self.assertEquals(form['destination'].value, '')
        self.assertEquals(form['categories'].value, '')

        form['name'] = 'Google'
        form['destination'] = 'https://google.com'
        response = form.submit().follow()
        response.mustcontain('<h1>Google</h1>')

        self.assertEquals(
            response.html.find(id='link_owner').text,
            'Fake Fakerly'
        )

    def test_create_link_external(self):
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
        response.mustcontain('<h1>Google</h1>')
        response.mustcontain('External')

        self.assertEquals(
            response.html.find(id='link_owner').text,
            'Fake Fakerly'
        )

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
        self.assertEqual(len(error_list.findChildren()), 2)

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
            reverse('link-detail', kwargs={'pk': existing_link.pk}),
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
        self.assertEqual(len(error_list.findChildren()), 1)

        form = response.form

        self.assertEquals(form['name'].value, '')
        self.assertEquals(form['description'].value,
                          'Another great mapping application')
        self.assertEquals(form['destination'].value, 'https://maps.bing.com')
        self.assertEquals(form['categories'].value, '')
