# (c) Crown Owned Copyright, 2016. Dstl.

from datetime import timedelta
from unittest import mock

from django.core.urlresolvers import reverse
from django.utils.timezone import now

from django_webtest import WebTest

from apps.links.tests.common import make_user, login_user
from apps.search.models import SearchTerm, SearchQuery


class TopSearches(WebTest):
    @classmethod
    def setUpTestData(cls):
        cls.user = make_user()

        now_time = now()

        cls.search_term_1 = SearchTerm.objects.create(query='mail')
        cls.search_term_2 = SearchTerm.objects.create(query='steve')
        cls.search_term_3 = SearchTerm.objects.create(query='cheese')
        cls.search_term_4 = SearchTerm.objects.create(query='google')
        cls.search_term_5 = SearchTerm.objects.create(query='internet')

        for t in range(0, 7):
            cls.search_q_1 = SearchQuery.objects.create(
                term=cls.search_term_1,
                user=cls.user,
                when=now_time - timedelta(days=t),
                results_length=8-t  # Going back in time, little less each day
            )

        for t in range(0, 6):
            cls.search_q_2 = SearchQuery.objects.create(
                term=cls.search_term_2,
                user=cls.user,
                when=now_time - timedelta(days=t),
                results_length=0
            )

        for t in range(0, 5):
            cls.search_q_3 = SearchQuery.objects.create(
                term=cls.search_term_3,
                user=cls.user,
                when=now_time - timedelta(days=t),
                results_length=0
            )

        for t in range(0, 4):
            cls.search_q_4 = SearchQuery.objects.create(
                term=cls.search_term_4,
                user=cls.user,
                when=now_time - timedelta(days=t),
                results_length=5-t  # Going back in time, little less each day
            )

        for t in range(0, 3):
            cls.search_q_5 = SearchQuery.objects.create(
                term=cls.search_term_5,
                user=cls.user,
                when=now_time - timedelta(days=t),
                results_length=0
            )

        # Throw in a query over 30 days ago which DID return some results, as
        # if the results had been deleted since then. Will count as unfulfilled
        with mock.patch('django.utils.timezone.now') as mock_now:
            # register usage 50 days ago
            mock_now.return_value = now_time - timedelta(days=50)
            cls.search_q_6 = SearchQuery.objects.create(
                term=cls.search_term_5,
                user=cls.user,
                results_length=2
            )

    def setUp(self):
        self.assertTrue(login_user(self, self.user))

    def test_top_searches_30_days(self):
        response = self.app.get(reverse('search-stats'))
        top_30_queries = response.html.find(
            None,
            {"id": "search-queries-top-30"}
        )
        search_queries_rows = top_30_queries.findChildren('tr')
        self.assertEquals(len(search_queries_rows), 6)

        self.assertIn('mail', search_queries_rows[1].text)
        self.assertIn('7', search_queries_rows[1].text)

        self.assertIn('steve', search_queries_rows[2].text)
        self.assertIn('6', search_queries_rows[2].text)

        self.assertIn('cheese', search_queries_rows[3].text)
        self.assertIn('5', search_queries_rows[3].text)

        self.assertIn('google', search_queries_rows[4].text)
        self.assertIn('4', search_queries_rows[4].text)

        self.assertIn('internet', search_queries_rows[5].text)
        self.assertIn('3', search_queries_rows[5].text)

    def test_top_unfulfilled_searches_30_days(self):
        response = self.app.get(reverse('search-stats'))
        top_30_unfulfilled_queries = response.html.find(
            None,
            {"id": "search-unfulfilled-queries-top-30"}
        )
        search_queries_rows = top_30_unfulfilled_queries.findChildren('tr')
        self.assertEquals(len(search_queries_rows), 4)

        self.assertIn('steve', search_queries_rows[1].text)
        self.assertIn('6', search_queries_rows[1].text)

        self.assertIn('cheese', search_queries_rows[2].text)
        self.assertIn('5', search_queries_rows[2].text)

        self.assertIn('internet', search_queries_rows[3].text)
        self.assertIn('3', search_queries_rows[3].text)
