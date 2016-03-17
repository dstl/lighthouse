# (c) Crown Owned Copyright, 2016. Dstl.

from django.core.urlresolvers import reverse

from django_webtest import WebTest

from ..models import Link
from .common import make_user, login_user


class LinkSearchResults(WebTest):
    @classmethod
    def setUpTestData(cls):
        cls.user = make_user()
        cls.link = Link.objects.create(
            name='Google',
            destination='https://google.com',
            description='Internet search',
            owner=cls.user,
            is_external=False,
        )
        cls.other_link = Link.objects.create(
            name='Google Mail',
            destination='https://mail.google.com',
            description='Internet email',
            owner=cls.user,
            is_external=True,
        )

    def setUp(self):
        self.assertTrue(login_user(self, self.user))

    def test_search_for_tool_shows_both(self):
        search_url = '%s?q=google' % reverse('search')
        response = self.app.get(search_url)
        results = response.html.find(id='search-results').findAll('li')
        self.assertEquals(len(results), 2)

    def test_search_for_first_shows_one(self):
        search_url = '%s?q=search' % reverse('search')
        response = self.app.get(search_url)
        results = response.html.find(id='search-results').findAll('li')
        self.assertEquals(len(results), 1)
        self.assertIn('Google', results[0].text)

    def test_search_for_second_shows_one(self):
        search_url = '%s?q=email' % reverse('search')
        response = self.app.get(search_url)
        results = response.html.find(id='search-results').findAll('li')
        self.assertEquals(len(results), 1)
        self.assertIn('Google Mail', results[0].text)

    def test_search_for_flibble_shows_none(self):
        search_url = '%s?q=flibble' % reverse('search')
        response = self.app.get(search_url)
        self.assertIsNone(response.html.find(id='search-results'))
