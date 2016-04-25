# (c) Crown Owned Copyright, 2016. Dstl.

from django.core.urlresolvers import reverse

from django_webtest import WebTest

from testing.common import make_user, login_user
from haystack.management.commands import rebuild_index


class UserSearchResults(WebTest):
    def setUp(self):
        self.user = make_user(
            userid='ant@0001.com',
            email='ant@dstl.gov.uk',
            name='Ant Anterton')

        self.box_user = make_user(
            userid='box@0001.com',
            email='box@dstl.gov.uk',
            name='Box Boxerly')

        self.chair_user = make_user(
            userid='chair@0001.com',
            email='chair@dstl.gov.uk',
            name='Chair Chairington')

        self.first_desk_user = make_user(
            userid='desk@0001.com',
            email='desk@dstl.gov.uk',
            name='Desk Deskworth')

        self.second_desk_user = make_user(
            userid='desk_desker@0001.com',
            email='desk_desker@dstl.gov.uk',
            name='Desk Desker')

        self.eagle_user = make_user(
            userid='eagle@0001.com',
            email='eagle@dstl.gov.uk',
            name='Eagle Eagerly')

        self.feather_user = make_user(
            userid='featherfeatherly',
            email='f@dstl.gov.uk',
            name='')

        self.assertTrue(login_user(self, self.user))

        rebuild_index.Command().handle(interactive=False, verbosity=0)

    def test_search_for_specific_name_returns_one(self):
        search_url = '%s?q=ant' % reverse('user-list')
        response = self.app.get(search_url)
        search_results_list = response.html.find(id='user-list')
        results = search_results_list.findAll('li')
        self.assertEquals(len(results), 1)
        self.assertIn('Ant Anterton', search_results_list.text)

    def test_search_for_email_address_returns_one(self):
        search_url = '%s?q=desk_desker@dstl.gov.uk' % reverse('user-list')
        response = self.app.get(search_url)
        search_results_list = response.html.find(id='user-list')
        results = search_results_list.findAll('li')
        self.assertEquals(len(results), 1)
        self.assertIn('Desk Desker', search_results_list.text)

    def test_search_for_common_name_returns_all(self):
        search_url = '%s?q=desk' % reverse('user-list')
        response = self.app.get(search_url)
        search_results_list = response.html.find(id='user-list')
        results = search_results_list.findAll('li')
        self.assertEquals(len(results), 2)
        self.assertIn('Desk Desker', search_results_list.text)
        self.assertIn('Desk Deskworth', search_results_list.text)

    def test_search_for_user_without_name_returns_one(self):
        search_url = '%s?q=featherfeatherly' % reverse('user-list')
        response = self.app.get(search_url)
        search_results_list = response.html.find(id='user-list')
        results = search_results_list.findAll('li')
        self.assertEquals(len(results), 1)
        self.assertIn('featherfeatherly', search_results_list.text)
