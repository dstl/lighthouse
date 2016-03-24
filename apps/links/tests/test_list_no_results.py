# (c) Crown Owned Copyright, 2016. Dstl.

from django.core.urlresolvers import reverse

from django_webtest import WebTest

from .common import generate_fake_links, login_user, make_user


class ListLinksWithNoResultsTest(WebTest):
    def setUp(self):
        self.logged_in_user = make_user()

        (self.el1,) = generate_fake_links(
            self.logged_in_user,
            count=1
        )

        (self.el2,) = generate_fake_links(
            self.logged_in_user,
            is_external=True,
            count=1
        )

        self.el1.categories.add('social')
        self.el1.save()

        self.el2.categories.add('mapping')
        self.el2.save()

        self.assertTrue(login_user(self, self.logged_in_user))

    def test_no_results_message(self):
        response = self.app.get(reverse('link-list'))

        form = response.forms['list-results']

        self.assertEquals(
            form.get('categories', index=0).id, 'categories-filter-social'
        )
        form.get('categories', index=0).checked = True

        self.assertEquals(
            form.get('types', index=0).id, 'types-filter-external'
        )
        form.get('types', index=0).checked = True

        response = form.submit()
        form = response.forms['list-results']

        tools_list_result_header = response.html.find(id="tools-header")

        self.assertEquals(
            len(response.html.findAll('li', {'class': 'link-list-item'})),
            0
        )

        self.assertEquals(
            tools_list_result_header.text,
            'No results found.'
        )

        self.assertIsNotNone(response.html.find(id="no-results-message"))
