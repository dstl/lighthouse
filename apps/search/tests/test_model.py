# (c) Crown Owned Copyright, 2016. Dstl.

from django.test import TestCase

from testing.common import make_user
from apps.search.models import SearchQuery, SearchTerm


class LinkSearchResults(TestCase):
    def setUp(self):
        self.user = make_user()

    def test_query_is_saved(self):
        st = SearchTerm.objects.create(
            query='test'
        )
        sq = SearchQuery()
        sq.term = st
        sq.results_length = 5
        sq.user = self.user
        sq.save()

        retrieved_term = SearchTerm.objects.all()[0]
        retrieved_query = SearchQuery.objects.all()[0]

        self.assertEquals(retrieved_term.query, 'test')
        self.assertEquals(retrieved_query.term, retrieved_term)
