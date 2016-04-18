# (c) Crown Owned Copyright, 2016. Dstl.

from django.core.urlresolvers import reverse

from django_webtest import WebTest

from testing.common import make_user, login_user
from apps.links.models import Link


class LinkTest(WebTest):
    def setUp(self):
        self.owner_user = make_user(
            userid='owner',
            email='fake2@dstl.gov.uk',
            name='Owner User')
        self.existing_link = Link(
            name='Wikimapia',
            description='A great mapping application',
            destination='https://wikimapia.org',
            owner=self.owner_user)
        self.existing_link.save()

        self.first_editor = make_user(
            userid='first_editor',
            email='editor_1@dstl.gov.uk',
            name='First Editor')
        self.second_editor = make_user(
            userid='second_editor',
            email='editor_2@dstl.gov.uk')

        self.assertTrue(login_user(self, self.first_editor))

    def test_edit_link_button_is_visible_to_non_owner(self):
        response = self.app.get(
            reverse('link-detail', kwargs={'pk': self.existing_link.pk}))

        edit_button = response.html.find(None, {'id': 'edit-button'})

        self.assertIsNotNone(edit_button)

    def test_edit_link_submit_works(self):
        form = self.app.get(
            reverse('link-edit', kwargs={'pk': self.existing_link.pk})).form

        self.assertEquals(form['name'].value, 'Wikimapia')
        self.assertEquals(form['description'].value,
                          'A great mapping application')
        self.assertEquals(form['destination'].value, 'https://wikimapia.org')

        form['name'].value = 'Bing Maps'
        form['description'].value = 'A brilliant free mapping application'
        form['destination'].value = 'https://maps.bing.com'

        response = form.submit().follow()

        self.assertIn('Bing Maps', response)
        self.assertNotIn('Wikimapia', response)
        self.assertIn('A brilliant free mapping application', response)
        self.assertNotIn('A great mapping application', response)
        self.assertIn('https://maps.bing.com', response)
        self.assertNotIn('https://wikimapia.org', response)

        owner_element = response.html.find(None, {'id': 'link_owner'})

        self.assertIn(self.owner_user.name, owner_element.text)
        self.assertIn(self.first_editor.name, owner_element.text)

    def test_editor_stack_stored(self):
        form = self.app.get(
            reverse('link-edit', kwargs={'pk': self.existing_link.pk})).form

        # Edit with the first editor
        self.assertEquals(form['name'].value, 'Wikimapia')
        self.assertEquals(form['description'].value,
                          'A great mapping application')
        self.assertEquals(form['destination'].value, 'https://wikimapia.org')

        form['name'].value = 'Bing Maps'
        form['description'].value = 'A brilliant free mapping application'
        form['destination'].value = 'https://maps.bing.com'

        response = form.submit()

        # Login as the second editor
        self.assertTrue(login_user(self, self.second_editor))

        form = self.app.get(
            reverse('link-edit', kwargs={'pk': self.existing_link.pk})).form

        # Edit with the second editor
        form['name'].value = 'Panoramio'
        form['description'].value = 'A super free mapping application'
        form['destination'].value = 'https://panoramio.com'
        # So we can make sure it works in both cases
        form['is_external'].select('True')

        response = form.submit().follow()

        self.assertIn('Panoramio', response)
        self.assertNotIn('Bing Maps', response)
        self.assertIn('A super free mapping application', response)
        self.assertNotIn('A brilliant mapping application', response)
        self.assertIn('https://panoramio.com', response)
        self.assertNotIn('https://maps.bing.com', response)

        owner_element = response.html.find(None, {'id': 'link_owner'})

        # Only show the most recent edit's author
        self.assertIn(str(self.owner_user), owner_element.text)
        self.assertNotIn(str(self.first_editor), owner_element.text)
        self.assertIn(str(self.second_editor), owner_element.text)

        # Store all the edits
        edits_oldest_first = self.existing_link.edits.order_by('date').all()
        self.assertEqual(edits_oldest_first[0].user, self.first_editor)
        self.assertEqual(edits_oldest_first[1].user, self.second_editor)
        self.assertTrue(
            edits_oldest_first[1].date > edits_oldest_first[0].date
        )
