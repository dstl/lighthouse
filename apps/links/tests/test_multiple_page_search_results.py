# (c) Crown Owned Copyright, 2016. Dstl.

from django.core.urlresolvers import reverse

from django_webtest import WebTest

from apps.links.models import Link
from testing.common import make_user, login_user, generate_fake_links
from haystack.management.commands import rebuild_index


class LinkSearchResultsMultiplePage(WebTest):
    def setUp(self):
        self.user = make_user()
        (self.el1, self.el2, self.el3,
            self.el4, self.el5, self.el6,
            self.el7, self.el8) = generate_fake_links(
            self.user,
            count=8
        )

        self.el1.categories.add('great')
        self.el2.categories.add('great')
        self.el3.categories.add('great')
        self.el4.categories.add('great')
        self.el5.categories.add('great')
        self.el6.categories.add('great')

        self.el7.is_external = True
        self.el7.save()

        self.el8.is_external = True
        self.el8.save()

        self.assertTrue(login_user(self, self.user))

        self.unfound_link_1 = Link.objects.create(
            name='Google Translate',
            destination='https://mail.google.com',
            description='Internet translation',
            owner=self.user,
        )

        self.unfound_link_2 = Link.objects.create(
            name='Google Mail',
            destination='https://translate.google.com',
            description='Internet email',
            owner=self.user,
        )

        rebuild_index.Command().handle(interactive=False, verbosity=0)

    def test_search_for_more_than_one_page_of_tools_maintains_length(self):
        search_url = '%s?q=Test' % reverse('link-list')
        response = self.app.get(search_url)
        results = response.html.find(id='link-results').findAll('li')
        self.assertEquals(len(results), 5)

        tools_list_result_header = response.html.find(id="tools-header")

        self.assertEquals(
            tools_list_result_header.text,
            'Showing page 1 of 2'
        )

        self.assertEquals(
            len(response.html.findAll('li', {'class': 'link-list-item'})),
            5
        )

        self.assertIsNotNone(response.html.find('ol', {'class': 'pagination'}))

        response = response.click(linkid="page-link-next")

        results = response.html.find(id='link-results').findAll('li')
        self.assertEquals(len(results), 3)

    def test_search_two_pages_of_tools_with_categories_maintains_length(self):
        search_url = '%s?q=Test&categories=great' % reverse('link-list')
        response = self.app.get(search_url)
        results = response.html.find(id='link-results').findAll('li')
        self.assertEquals(len(results), 5)

        tools_list_result_header = response.html.find(id="tools-header")

        self.assertEquals(
            tools_list_result_header.text,
            'Showing page 1 of 2'
        )

        self.assertEquals(
            len(response.html.findAll('li', {'class': 'link-list-item'})),
            5
        )

        self.assertIsNotNone(response.html.find('ol', {'class': 'pagination'}))

        response = response.click(linkid="page-link-next")

        results = response.html.find(id='link-results').findAll('li')
        self.assertEquals(len(results), 1)

    def test_search_two_pages_of_tools_with_internal_maintains_length(self):
        surl = reverse('link-list')
        search_url = '%s?q=Test&types=internal' % surl
        response = self.app.get(search_url)
        results = response.html.find(id='link-results').findAll('li')
        self.assertEquals(len(results), 5)

        tools_list_result_header = response.html.find(id="tools-header")

        self.assertEquals(
            tools_list_result_header.text,
            'Showing page 1 of 2'
        )

        self.assertEquals(
            len(response.html.findAll('li', {'class': 'link-list-item'})),
            5
        )

        self.assertIsNotNone(response.html.find('ol', {'class': 'pagination'}))

        response = response.click(linkid="page-link-next")

        results = response.html.find(id='link-results').findAll('li')
        self.assertEquals(len(results), 3)
