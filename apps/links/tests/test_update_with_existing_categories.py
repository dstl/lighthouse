# (c) Crown Owned Copyright, 2016. Dstl.
from django.core.urlresolvers import reverse
from apps.links.models import Link
from .common import make_user, login_user

from django_webtest import WebTest


class CategorisedLinksWithCategoriesUpdateTest(WebTest):
    def setUp(self):
        self.logged_in_user = make_user()
        self.assertTrue(login_user(self, self.logged_in_user))

        self.existing_link = Link(
            name='Tweetbot',
            description='A great twitter application',
            destination='https://tweetbot.com',
            owner=self.logged_in_user,)
        self.existing_link.save()
        self.existing_link.categories.add('social')
        self.existing_link.categories.add('imagery')
        self.existing_link.save()

    def test_update_link_with_existing_categories_render(self):
        form = self.app.get(
            reverse('link-edit', kwargs={'pk': self.existing_link.pk})).form

        self.assertTrue(form.get('categories', index=1).checked)
        self.assertIn(
            'Social',
            form.html.findAll(
                'label', {'class': 'link-category-label'}
            )[0].text,
        )
        self.assertTrue(form.get('categories', index=1).checked)
        self.assertIn(
            'Imagery',
            form.html.findAll(
                'label', {'class': 'link-category-label'}
            )[1].text,
        )
        self.assertEquals(form.get('categories', index=2).value, '')

    def test_update_link_with_existing_categories_submit(self):
        form = self.app.get(
            reverse('link-edit', kwargs={'pk': self.existing_link.pk})).form

        form.get('categories', index=1).checked = False  # Imagery

        response = form.submit().follow()

        self.assertIn('Tweetbot', response.html.find('h1').text)

        self.assertIn(
            'Fake Fakerly',
            response.html.find(id='link_owner').text,
        )

        # To find all the categories. then map to get `text`
        categories = [element.text for element in response.html.findAll(
            None, {"class": "link-category"})
        ]

        assert "Social" in categories
        assert "Imagery" not in categories

        self.assertEquals(len(categories), 1)
