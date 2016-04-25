# (c) Crown Owned Copyright, 2016. Dstl.

from django.core.urlresolvers import reverse

from django_webtest import WebTest

from testing.common import make_user, login_user, generate_fake_links


class LighthouseGoToTest(WebTest):
    def test_lighthouse_edit_page_has_no_destination_box(self):
        self.logged_in_user = make_user()
        self.app.get(reverse('login'))

        self.assertTrue(login_user(self, self.logged_in_user))

        response = self.app.get(reverse('link-edit', kwargs={'pk': 1}))

        dest_input = response.html.find('input', {'name': 'destination'})

        self.assertEqual(dest_input.attrs['type'], 'hidden')

    def test_lighthouse_api_edit_page_has_no_destination_box(self):
        self.logged_in_user = make_user()
        self.app.get(reverse('login'))

        self.assertTrue(login_user(self, self.logged_in_user))

        response = self.app.get(reverse('link-edit', kwargs={'pk': 2}))

        dest_input = response.html.find('input', {'name': 'destination'})

        self.assertEqual(dest_input.attrs['type'], 'hidden')

    def test_lighthouse_api_edit_page_can_submit(self):
        self.logged_in_user = make_user()
        self.app.get(reverse('login'))

        self.assertTrue(login_user(self, self.logged_in_user))

        response = self.app.get(reverse('link-edit', kwargs={'pk': 2}))
        form = response.form

        new_desc = 'I love the Lighthouse API'
        form['description'] = new_desc

        response = form.submit().follow()

        error_summary = response.html.find('div', {"class": "error-summary"})
        self.assertIsNone(error_summary)

        description = response.html.find(
            'div', {"class": "markdown-content"})

        self.assertIn(new_desc, description.text)

    def test_normal_edit_page_has_destination_box(self):
        self.logged_in_user = make_user()
        self.app.get(reverse('login'))
        link, = generate_fake_links(owner=self.logged_in_user)

        self.assertTrue(login_user(self, self.logged_in_user))

        response = self.app.get(reverse('link-edit', kwargs={'pk': link.id}))

        dest_input = response.html.find('input', {'name': 'destination'})

        self.assertEqual(dest_input.attrs['type'], 'url')
