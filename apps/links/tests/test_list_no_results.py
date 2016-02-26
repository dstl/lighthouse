from django.core.urlresolvers import reverse
from apps.users.models import User
from .common import generate_fake_links

from django_webtest import WebTest


class ListLinksWithNoResultsTest(WebTest):
    def setUp(self):
        self.logged_in_user = User(
            fullName='Fake Fakerly',
            phone='555-2187',
            email='fake@dstl.gov.uk')
        self.logged_in_user.save()

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

        response = self.app.get(reverse('login-view'))

        response = response.click('Fake Fakerly').follow()

        self.assertEquals(response.html.h1.text, 'Fake Fakerly')

    def test_no_results_message(self):
        response = self.app.get(reverse('link-list'))

        form = response.form

        self.assertEquals(
            form.get('categories', index=0).id, 'categories-filter-social'
        )
        form.get('categories', index=0).checked = True

        self.assertEquals(
            form.get('types', index=0).id, 'types-filter-external'
        )
        form.get('types', index=0).checked = True

        response = form.submit()
        form = response.form

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
