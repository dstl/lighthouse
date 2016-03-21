# (c) Crown Owned Copyright, 2016. Dstl.

from datetime import datetime
from unittest import mock

from django.core.urlresolvers import reverse

from django_webtest import WebTest
from django.utils.timezone import make_aware

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
        with mock.patch('django.utils.timezone.now') as mock_now:
            # register usage on a specific day
            mock_now.return_value = make_aware(datetime(2016, 3, 1, 10, 0, 0))
            search_url = '%s?q=google' % reverse('search')
            response = self.app.get(search_url)

        results = response.html.find(id='search-results').findAll('li')
        self.assertEquals(len(results), 2)

        response = self.app.get(reverse('search-stats'))
        search_queries_table = response.html.find(
            None,
            {"id": "search-queries"}
        )
        search_queries_rows = search_queries_table.findChildren('tr')
        self.assertEquals(len(search_queries_rows), 2)

        self.assertIn('google', search_queries_rows[1].text)
        self.assertIn('2', search_queries_rows[1].text)
        self.assertIn('01/03/2016, 10:00', search_queries_rows[1].text)

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

    def test_search_twice_with_different_terms(self):
        with mock.patch('django.utils.timezone.now') as mock_now:
            # register usage on a specific day
            mock_now.return_value = make_aware(datetime(2016, 3, 1, 10, 0, 0))
            search_url = '%s?q=flibble' % reverse('search')
            response = self.app.get(search_url)
            self.assertIsNone(response.html.find(id='search-results'))

            mock_now.return_value = make_aware(datetime(2016, 3, 1, 10, 2, 0))
            search_url = '%s?q=google' % reverse('search')
            response = self.app.get(search_url)

        results = response.html.find(id='search-results').findAll('li')
        self.assertEquals(len(results), 2)

        response = self.app.get(reverse('search-stats'))
        search_queries_table = response.html.find(
            None,
            {"id": "search-queries"}
        )
        search_queries_rows = search_queries_table.findChildren('tr')
        self.assertEquals(len(search_queries_rows), 3)

        self.assertIn('google', search_queries_rows[1].text)
        self.assertIn('2', search_queries_rows[1].text)
        self.assertIn('01/03/2016, 10:02', search_queries_rows[1].text)

        self.assertIn('flibble', search_queries_rows[2].text)
        self.assertIn('0', search_queries_rows[2].text)
        self.assertIn('01/03/2016, 10:00', search_queries_rows[2].text)
