from django.core.urlresolvers import reverse
from apps.users.models import User
from .common import generate_fake_links

from django_webtest import WebTest


class ListLinksWithNoCategoriesTest(WebTest):
    def setUp(self):
        self.logged_in_user = User(
            fullName='Fake Fakerly',
            phone='555-2187',
            email='fake@dstl.gov.uk')
        self.logged_in_user.save()

        el1, el2 = generate_fake_links(
            self.logged_in_user,
            count=2
        )

        self.existing_link_1 = el1

        self.existing_link_2 = el2

        response = self.app.get(reverse('login-view'))

        response = response.click('Fake Fakerly').follow()

        self.assertEquals(response.html.h1.text, 'Fake Fakerly')

    def test_one_page(self):
        response = self.app.get(reverse('link-list'))

        # They should appear with the newest one at the top by the default
        # sorting method

        self.assertIsNone(response.html.find('ol', {'class': 'pagination'}))

        self.assertIn(
            self.existing_link_2.name,
            response.html.findAll(
                'li',
                {'class': 'link-list-item'}
            )[0].text,
        )

        self.assertIn(
            self.existing_link_1.name,
            response.html.findAll(
                'li',
                {'class': 'link-list-item'}
            )[1].text,
        )

    def test_two_pages(self):
        el3, el4, el5, el6 = generate_fake_links(
            self.logged_in_user,
            start=3,
            count=4
        )

        response = self.app.get(reverse('link-list'))

        self.assertEquals(
            len(response.html.findAll('li', {'class': 'link-list-item'})),
            5
        )

        self.assertIsNotNone(response.html.find('ol', {'class': 'pagination'}))

        self.assertIn(
            el6.name,
            response.html.findAll(
                'li',
                {'class': 'link-list-item'}
            )[0].text,
        )

        self.assertIn(
            el5.name,
            response.html.findAll(
                'li',
                {'class': 'link-list-item'}
            )[1].text,
        )

        self.assertIn(
            el4.name,
            response.html.findAll(
                'li',
                {'class': 'link-list-item'}
            )[2].text,
        )

        self.assertIn(
            el3.name,
            response.html.findAll(
                'li',
                {'class': 'link-list-item'}
            )[3].text,
        )

        self.assertIn(
            self.existing_link_2.name,
            response.html.findAll(
                'li',
                {'class': 'link-list-item'}
            )[4].text,
        )