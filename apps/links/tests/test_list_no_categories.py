from django.core.urlresolvers import reverse
from apps.users.models import User
from apps.links.models import Link

from django_webtest import WebTest


class ListLinksWithNoCategoriesTest(WebTest):
    def setUp(self):
        self.logged_in_user = User(
            fullName='Fake Fakerly',
            phone='555-2187',
            email='fake@dstl.gov.uk')
        self.logged_in_user.save()

        self.existing_link_1 = Link(
            name='Wikimapia',
            description='A great mapping application',
            destination='https://wikimapia.org',
            owner=self.logged_in_user,
            is_external=False)
        self.existing_link_1.save()

        self.existing_link_2 = Link(
            name='Twitter',
            description='A thing for Social Media stuff',
            destination='https://twitter.com',
            owner=self.logged_in_user,
            is_external=False)
        self.existing_link_2.save()

        response = self.app.get(reverse('login-view'))

        response = response.click('Fake Fakerly').follow()

        self.assertEquals(response.html.h1.text, 'Fake Fakerly')

    def test_one_page(self):
        response = self.app.get(reverse('link-list'))

        # They should appear with the newest one at the top by the default
        # sorting method

        self.assertIsNone(response.html.find('ol', {'class': 'pagination'}))

        self.assertEquals(
            response.html.findAll(
                'li',
                {'class': 'link-list-item'}
            )[0].text,
            'Twitter'
        )

        self.assertEquals(
            response.html.findAll(
                'li',
                {'class': 'link-list-item'}
            )[1].text,
            'Wikimapia'
        )

    def test_two_pages(self):
        existing_link_3 = Link(
            name='Third Link',
            description='Test',
            destination='https://test3.org',
            owner=self.logged_in_user,
            is_external=False)
        existing_link_3.save()

        existing_link_4 = Link(
            name='Fourth Link',
            description='Test',
            destination='https://test4.org',
            owner=self.logged_in_user,
            is_external=False)
        existing_link_4.save()

        existing_link_5 = Link(
            name='Fifth Link',
            description='Test',
            destination='https://test5.org',
            owner=self.logged_in_user,
            is_external=False)
        existing_link_5.save()

        existing_link_6 = Link(
            name='Sixth Link',
            description='Test',
            destination='https://test6.org',
            owner=self.logged_in_user,
            is_external=False)
        existing_link_6.save()

        response = self.app.get(reverse('link-list'))

        self.assertEquals(
            len(response.html.findAll('li', {'class': 'link-list-item'})),
            5
        )

        self.assertIsNotNone(response.html.find('ol', {'class': 'pagination'}))

        self.assertEquals(
            response.html.findAll(
                'li',
                {'class': 'link-list-item'}
            )[0].text,
            'Sixth Link'
        )

        self.assertEquals(
            response.html.findAll(
                'li',
                {'class': 'link-list-item'}
            )[1].text,
            'Fifth Link'
        )

        self.assertEquals(
            response.html.findAll(
                'li',
                {'class': 'link-list-item'}
            )[2].text,
            'Fourth Link'
        )

        self.assertEquals(
            response.html.findAll(
                'li',
                {'class': 'link-list-item'}
            )[3].text,
            'Third Link'
        )

        self.assertEquals(
            response.html.findAll(
                'li',
                {'class': 'link-list-item'}
            )[4].text,
            'Twitter'
        )
