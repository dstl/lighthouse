# (c) Crown Owned Copyright, 2016. Dstl.

from django.core.urlresolvers import reverse

from django_webtest import WebTest

from testing.common import generate_fake_links, login_user, make_user
from haystack.management.commands import rebuild_index


class ListFavouriteLinksTest(WebTest):
    def setUp(self):
        self.logged_in_user = make_user()

        (self.el1, self.el2, self.el3,) = generate_fake_links(
            self.logged_in_user,
            count=3
        )

        self.el1.categories.add('mapping')
        self.el1.save()

        self.el2.categories.add('mapping')
        self.el2.save()

        self.el3.categories.add('social')
        self.el3.save()

        self.el3.name = 'Unique'
        self.el3.save()

        self.logged_in_user.favourites.add(self.el2)
        self.logged_in_user.favourites.add(self.el3)

        self.assertTrue(login_user(self, self.logged_in_user))

        rebuild_index.Command().handle(interactive=False, verbosity=0)

    def test_favourite_checkbox(self):
        response = self.app.get(reverse('link-list'))

        filterEl = response.html.find(id='categories-filter')

        favouritesLbl = filterEl.find(attrs={'for': 'filter-favourites'})
        favouritesCheckbox = filterEl.find(id='filter-favourites')
        self.assertIsNotNone(favouritesLbl)
        self.assertIsNotNone(favouritesCheckbox)
        self.assertEquals(favouritesCheckbox.attrs['value'], 'true')
        self.assertFalse('checked' in favouritesCheckbox.attrs)

    def test_favourite_filter(self):
        response = self.app.get(reverse('link-list'))

        form = response.forms['list-results']

        self.assertEquals(
            form.get('favourites', index=0).id, 'filter-favourites'
        )
        form.get('favourites', index=0).checked = True

        response = form.submit()
        form = response.forms['list-results']

        self.assertEquals(
            len(response.html.findAll('li', {'class': 'link-list-item'})),
            2
        )

        self.assertIsNone(response.html.find('ol', {'class': 'pagination'}))

        self.assertIn(
            self.el3.name,
            response.html.findAll(
                'li',
                {'class': 'link-list-item'}
            )[0].text,
        )

        self.assertIn(
            self.el2.name,
            response.html.findAll(
                'li',
                {'class': 'link-list-item'}
            )[1].text,
        )

        self.assertTrue(form.get('favourites', index=0).checked)

    def test_favourite_and_query_filter(self):
        response = self.app.get(reverse('link-list'))

        form = response.forms['list-results']

        self.assertEquals(
            form.get('favourites', index=0).id, 'filter-favourites'
        )
        form.get('favourites', index=0).checked = True

        form['q'] = self.el3.name

        response = form.submit()
        form = response.forms['list-results']

        self.assertEquals(
            len(response.html.findAll('li', {'class': 'link-list-item'})),
            1
        )

        self.assertIsNone(response.html.find('ol', {'class': 'pagination'}))

        self.assertIn(
            self.el3.name,
            response.html.findAll(
                'li',
                {'class': 'link-list-item'}
            )[0].text,
        )

        self.assertTrue(form.get('favourites', index=0).checked)
