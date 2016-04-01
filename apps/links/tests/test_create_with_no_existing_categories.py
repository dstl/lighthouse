# (c) Crown Owned Copyright, 2016. Dstl.

from django.core.urlresolvers import reverse

from django_webtest import WebTest

from testing.common import make_user, login_user


class CategorisedLinksWithNoCategoriesTest(WebTest):
    def setUp(self):
        self.logged_in_user = make_user()
        self.assertTrue(login_user(self, self.logged_in_user))

    def test_create_link_with_new_category(self):
        response = self.app.get(reverse('link-create'))
        form = response.form

        existing_categories_label = response.html.find(
            id='existing-categories-label'
        )

        self.assertIsNone(existing_categories_label)

        self.assertEquals(form['name'].value, '')
        self.assertEquals(form['description'].value, '')
        self.assertEquals(form['destination'].value, '')

        form['name'] = 'Google Maps'
        form['destination'] = 'https://google.com'
        form['categories'] = 'mapping, geospatial'

        response = form.submit().follow()
        self.assertIn('Google Maps', response.html.find('h1').text)

        self.assertIn(
            'Fake Fakerly',
            response.html.find(id='link_owner').text,
        )

        # To find all the categories. then map to get `text`
        categories = [element.text for element in response.html.findAll(
            None, {"class": "link-category"})
        ]

        assert "Mapping" in categories
        assert "Geospatial" in categories
