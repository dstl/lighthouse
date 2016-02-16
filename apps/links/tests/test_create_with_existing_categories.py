from django.core.urlresolvers import reverse
from apps.links.models import Link
from apps.users.models import User

from django_webtest import WebTest


class CategorisedLinksWithCategoriesTest(WebTest):
    def setUp(self):
        self.logged_in_user = User(
            fullName='Fake Fakerly',
            phone='555-2187',
            email='fake@dstl.gov.uk')
        self.logged_in_user.save()

        response = self.app.get(reverse('login-view'))

        response = response.click('Fake Fakerly').follow()

        self.assertEquals(response.html.h1.text, 'Fake Fakerly')

        existing_link = Link(
            name='Tweetbot',
            description='A great twitter application',
            destination='https://tweetbot.com',
            owner=self.logged_in_user,)
        existing_link.save()
        existing_link.categories.add('social')
        existing_link.categories.add('imagery')
        existing_link.save()

    def test_create_link_with_existing_categories_render(self):
        form = self.app.get(reverse('link-create')).form

        self.assertEquals(form['name'].value, '')
        self.assertEquals(form['description'].value, '')
        self.assertEquals(form['destination'].value, '')

        category_label_values = [
            element.text for element in
            form.html.findAll('label', {"class": "link-category-label"})
        ]

        category_input_values = [
            element.get('value') for element in
            form.html.findAll('input', {"class": "link-category-checkbox"})
        ]

        assert "Social" in category_label_values
        assert "Imagery" in category_label_values

        assert "social" in category_input_values
        assert "imagery" in category_input_values

        self.assertEquals(len(category_label_values), 2)
        self.assertEquals(len(category_input_values), 2)

    def test_create_link_with_existing_categories_submit(self):
        form = self.app.get(reverse('link-create')).form

        form['name'] = 'Google Maps'
        form['destination'] = 'https://google.com'
        # form['categories'] = 'mapping, geospatial'

        self.assertFalse(form.get('categories', index=0).checked)  # Social
        self.assertFalse(form.get('categories', index=1).checked)  # Imagery
        self.assertEquals(form.get('categories', index=2).value, '')

        form.get('categories', index=1).checked = True  # Imagery

        response = form.submit().follow()

        response.mustcontain('<h1>Google Maps</h1>')

        self.assertEquals(
            response.html.find(id='link_owner').text,
            'Fake Fakerly'
        )

        # To find all the categories. then map to get `text`
        categories = [element.text for element in response.html.findAll(
            None, {"class": "link-category"})
        ]

        assert "Imagery" in categories

        self.assertEquals(len(categories), 1)
