from django.core.urlresolvers import reverse
from apps.users.models import User
from .common import generate_fake_links

from django_webtest import WebTest


class ListLinksWithExternalityTest(WebTest):
    def setUp(self):
        self.logged_in_user = User(
            fullName='Fake Fakerly',
            phone='555-2187',
            email='fake@dstl.gov.uk')
        self.logged_in_user.save()

        self.el1, self.el2 = generate_fake_links(
            self.logged_in_user,
            count=2,
            is_external=True
        )

        self.el3, self.el4, self.el5 = generate_fake_links(
            self.logged_in_user,
            start=3,
            count=3
        )

        # Note: the generator expects to send out a tuple, so allow that.
        (self.el6,) = generate_fake_links(
            self.logged_in_user,
            start=6,
            count=1,
            is_external=True
        )

        (self.el7,) = generate_fake_links(
            self.logged_in_user,
            start=7,
            count=1
        )

        self.el1.categories.add('mapping')
        self.el1.categories.add('social')
        self.el1.save()

        self.el2.categories.add('mapping')
        self.el2.save()

        self.el3.categories.add('social')
        self.el3.save()

        self.el4.categories.add('geospatial')
        self.el4.save()

        self.el5.categories.add('imagery')
        self.el5.save()

        self.el6.categories.add('geospatial')
        self.el6.categories.add('mapping')
        self.el6.save()

        self.el7.categories.add('social')
        self.el7.categories.add('mapping')
        self.el7.save()

        response = self.app.get(reverse('login-view'))

        response = response.click('Fake Fakerly').follow()

        self.assertEquals(response.html.h1.text, 'Fake Fakerly')

    def test_external_internal_printed(self):
        response = self.app.get(reverse('link-list'))

        self.assertIn(
            self.el7.name,
            response.html.findAll(
                'li',
                {'class': 'link-list-item'}
            )[0].text,
        )

        self.assertIn(
            'Internal',
            response.html.findAll(
                'li',
                {'class': 'link-list-item'}
            )[0].text,
        )

        self.assertIn(
            self.el6.name,
            response.html.findAll(
                'li',
                {'class': 'link-list-item'}
            )[1].text,
        )

        self.assertIn(
            'External',
            response.html.findAll(
                'li',
                {'class': 'link-list-item'}
            )[1].text,
        )
