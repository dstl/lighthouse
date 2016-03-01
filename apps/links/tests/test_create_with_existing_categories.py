# (c) Crown Owned Copyright, 2016. Dstl.
from django.core.urlresolvers import reverse
from apps.links.models import Link
from apps.users.models import User

from django_webtest import WebTest


class CategorisedLinksWithCategoriesTest(WebTest):
    def setUp(self):
        self.logged_in_user = User(
            slug='user0001',
            username='Fake Fakerly',
            phone='555-2187',
            email='fake@dstl.gov.uk')
        self.logged_in_user.save()

        response = self.app.get(reverse('login-view'))
        response = response.click('user0001').follow()
        user_id = response.html.find_all(
                'span', attrs={'class': 'user_id'}
            )[0].text
        self.assertEquals(user_id, 'user0001')

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
        response = self.app.get(reverse('link-create'))
        form = response.form

        existing_categories_label = response.html.find(
            id='existing-categories-label'
        )

        self.assertIsNotNone(existing_categories_label)

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

        self.assertFalse(form.get('categories', index=0).checked)
        self.assertEquals(
            form.html.findAll(
                'label', {'class': 'link-category-label'}
            )[0].text,
            'Social'
        )
        self.assertFalse(form.get('categories', index=1).checked)
        self.assertEquals(
            form.html.findAll(
                'label', {'class': 'link-category-label'}
            )[1].text,
            'Imagery'
        )
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

    def test_create_link_with_mixed_categories_submit(self):
        form = self.app.get(reverse('link-create')).form

        form['name'] = 'Google Maps'
        form['destination'] = 'https://google.com'

        form.get('categories', index=1).checked = True  # Imagery
        form.get('categories', index=2).value = 'mapping'

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
        assert "Mapping" in categories

        self.assertEquals(len(categories), 2)

        form = self.app.get(reverse('link-create')).form

        self.assertFalse(form.get('categories', index=0).checked)
        self.assertEquals(
            form.html.findAll(
                'label', {'class': 'link-category-label'}
            )[0].text,
            'Social'
        )
        self.assertFalse(form.get('categories', index=1).checked)
        self.assertEquals(
            form.html.findAll(
                'label', {'class': 'link-category-label'}
            )[1].text,
            'Imagery'
        )
        self.assertFalse(form.get('categories', index=2).checked)
        self.assertEquals(
            form.html.findAll(
                'label', {'class': 'link-category-label'}
            )[2].text,
            'Mapping'
        )
        self.assertEquals(form.get('categories', index=3).value, '')
