# (c) Crown Owned Copyright, 2016. Dstl.
from django.core.urlresolvers import reverse
from testing.common import login_user, make_user, generate_fake_links

from django_webtest import WebTest


class FavouriteLinksTest(WebTest):
    def setUp(self):
        self.logged_in_user = make_user()
        self.assertTrue(login_user(self, self.logged_in_user))

        self.el1, = generate_fake_links(
            self.logged_in_user,
            count=1,
            is_external=True
        )

    def test_user_can_add_link_to_favourites(self):
        self.assertNotIn(self.el1, self.logged_in_user.favourites.all())

        def get_elements(response):
            in_favourites_status = response.html.find(
                None,
                {"id": "in-favourites-message"}
            )
            not_in_favourites_status = response.html.find(
                None,
                {"id": "not-in-favourites-message"}
            )
            remove_from_favs_button = response.html.find(
                None,
                {"id": "remove-from-favourites"}
            )
            add_to_favs_button = response.html.find(
                None,
                {"id": "add-to-favourites"}
            )
            return (
                    in_favourites_status,
                    not_in_favourites_status,
                    remove_from_favs_button,
                    add_to_favs_button,
                    )

        response = self.app.get(
            reverse('link-detail', kwargs={"pk": self.el1.pk})
        )

        # Make sure it's not there
        (in_favourites_status, not_in_favourites_status,
         remove_from_favs_button, add_to_favs_button,) = get_elements(response)

        self.assertIsNone(in_favourites_status)
        self.assertIsNotNone(not_in_favourites_status)
        self.assertIsNone(remove_from_favs_button)
        self.assertIsNotNone(add_to_favs_button)

        # Now add it
        form = response.form

        response = form.submit().follow()

        (in_favourites_status, not_in_favourites_status,
         remove_from_favs_button, add_to_favs_button,) = get_elements(response)

        self.assertIsNotNone(in_favourites_status)
        self.assertIsNone(not_in_favourites_status)
        self.assertIsNotNone(remove_from_favs_button)
        self.assertIsNone(add_to_favs_button)

        # Now remove it
        form = response.form

        response = form.submit().follow()

        (in_favourites_status, not_in_favourites_status,
         remove_from_favs_button, add_to_favs_button,) = get_elements(response)

        self.assertIsNone(in_favourites_status)
        self.assertIsNotNone(not_in_favourites_status)
        self.assertIsNone(remove_from_favs_button)
        self.assertIsNotNone(add_to_favs_button)
