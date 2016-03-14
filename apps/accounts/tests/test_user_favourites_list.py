# (c) Crown Owned Copyright, 2016. Dstl.
from django.core.urlresolvers import reverse
from testing.common import login_user, make_user, generate_fake_links

from django_webtest import WebTest


class UserFavouriteLinksListTest(WebTest):
    def setUp(self):
        self.logged_in_user = make_user()
        self.assertTrue(login_user(self, self.logged_in_user))

        self.el1, self.el2, = generate_fake_links(
            self.logged_in_user,
            count=2,
            is_external=True
        )

        self.logged_in_user.favourites.add(self.el1)
        self.logged_in_user.favourites.add(self.el2)

    def test_list_contains_favourites(self):
        response = self.app.get(reverse(
            'user-detail',
            kwargs={'slug': self.logged_in_user.slug}))

        fav_list = response.html.find(None, {'id': 'favourites-list'})

        self.assertIsNotNone(fav_list)

        fav_list_items = fav_list.findChildren('li')

        self.assertEqual(len(fav_list_items), 2)

        self.assertIn(self.el1.name, fav_list_items[0].text)
        self.assertIn(self.el2.name, fav_list_items[1].text)
