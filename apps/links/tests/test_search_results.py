# (c) Crown Owned Copyright, 2016. Dstl.

import csv
from datetime import datetime
from unittest import mock

from django.core.urlresolvers import reverse
from django.utils.timezone import make_aware

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
        cls.other_link = Link.objects.create(
            name='Google Chat',
            destination='https://chat.google.com',
            description='Internet chat',
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
        self.assertEquals(len(results), 3)

        response = self.app.get(reverse('search-stats'))
        search_queries_table = response.html.find(
            None,
            {"id": "latest-20-searches"}
        )
        search_queries_rows = search_queries_table.findChildren('tr')
        self.assertEquals(len(search_queries_rows), 2)

        self.assertIn('google', search_queries_rows[1].text)
        self.assertIn('3', search_queries_rows[1].text)
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
            search_url = '%s?q=chat' % reverse('search')
            response = self.app.get(search_url)

        results = response.html.find(id='search-results').findAll('li')
        self.assertEquals(len(results), 1)

        response = self.app.get(reverse('search-stats'))
        search_queries_table = response.html.find(
            None,
            {"id": "latest-20-searches"}
        )
        search_queries_rows = search_queries_table.findChildren('tr')
        self.assertEquals(len(search_queries_rows), 3)

        self.assertIn('chat', search_queries_rows[1].text)
        self.assertIn('1', search_queries_rows[1].text)
        self.assertIn('01/03/2016, 10:02', search_queries_rows[1].text)

        self.assertIn('flibble', search_queries_rows[2].text)
        self.assertIn('0', search_queries_rows[2].text)
        self.assertIn('01/03/2016, 10:00', search_queries_rows[2].text)

        csv_download_link = response.html.find(
            None,
            {"id": "csv-download-all"}
        )

        self.assertEquals(
            reverse('search-stats-csv'),
            csv_download_link.get('href')
        )
        self.assertIsNotNone(csv_download_link)

    def test_search_stats_csv(self):
        self.test_search_twice_with_different_terms()

        response = self.app.get(reverse('search-stats-csv'))
        lines = response.body.decode().split("\r\n")
        dialect = csv.Sniffer().sniff(response.body.decode())
        reader = csv.DictReader(lines, dialect=dialect)

        row = next(reader)
        self.assertEquals(row, {
            'User': 'user0001com',
            'Date': '2016-03-01 10:00:00',
            'Term': 'flibble',
            'Number of Results': '0',
        })

        row = next(reader)
        self.assertEquals(row, {
            'User': 'user0001com',
            'Date': '2016-03-01 10:02:00',
            'Term': 'chat',
            'Number of Results': '1',
        })
