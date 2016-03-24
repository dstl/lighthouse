# (c) Crown Owned Copyright, 2016. Dstl.

from django.core.urlresolvers import reverse

from django_webtest import WebTest

from apps.users.models import User
from apps.teams.models import Team
from apps.organisations.models import Organisation


class UserWebTest(WebTest):

    #   We want to test that a user who is missing a username is redirected
    #   to the update user profile page
    def test_user_missing_data_redirected(self):
        #   This user doesn't have a username
        u = User(slug='user0001com', original_slug='user@0001.com')
        u.save()

        #   Log in as user
        form = self.app.get(reverse('login-view')).form
        form['slug'] = 'user0001com'
        response = form.submit().follow()

        #   Check that the add display name text is shown
        self.assertIn(
            'add a display name',
            response.html.find(
                None, {"class": "user_id"}
            ).text
        )

        #   Check that the link in the nav is heading to the right place
        self.assertEquals(
            response.html.find(
                'span', attrs={'data-slug': u.slug}
            ).find('a').attrs['href'],
            '/users/' + str(u.slug) + '/update-profile'
        )

        #   We should now be on the user needs to add information page
        self.assertEquals(
            response.html.find(
                'h3',
                attrs={'class': 'error-summary-heading'}
            ).text,
            'Please add a username'
        )

    #   Meanwhile a user who has a username but no teams will end up
    #   at the page asking for them to enter additional team information
    def test_user_has_username_but_no_teams_redirected(self):
        #   This user has a username
        u = User(
            slug='user0001com',
            original_slug='user@0001.com',
            username='User 0001'
        )
        u.save()

        #   Log in as user
        form = self.app.get(reverse('login-view')).form
        form['slug'] = 'user0001com'
        response = form.submit().follow()

        #   Check that the join a team text is shown
        self.assertIn(
            'join a team',
            response.html.find(
                None, {"class": "user_id"}
            ).text
        )

        #   Check that the link in the nav is heading to the right place
        self.assertEquals(
            response.html.find(
                'span', attrs={'data-slug': u.slug}
            ).find('a').attrs['href'],
            '/users/' + str(u.slug) + '/update-profile/teams'
        )

        #   Make sure we *don't* have an alert summary heading
        self.assertEquals(
            response.html.find(
                'h3',
                attrs={'class': 'error-summary-heading'}
            ).text,
            'Please add additional team information'
        )

    #   A user may have username, teams but still missing the extra information
    #   they will get an alert bell notification and link to update their
    #   profile.
    def test_user_has_username_teams_no_extra_info_redirected(self):
        #   This user has a username and teams
        o = Organisation(name='org0001')
        o.save()
        t = Team(name='team0001', organisation=o)
        t.save()
        u = User(
            slug='user0001com',
            original_slug='user@0001.com',
            username='User 0001'
        )
        u.save()
        u.teams.add(t)
        u.save()

        #   Log in as user
        form = self.app.get(reverse('login-view')).form
        form['slug'] = 'user0001com'
        response = form.submit().follow()

        #   Check that the add more details text is shown
        self.assertIn(
            'enter more details',
            response.html.find(
                None, {"class": "user_id"}
            ).text
        )

        #   Check that the link in the nav is heading to the right place
        self.assertIn(
            '/users/user0001com/update-profile',
            response.html.find(
                'span', attrs={'data-slug': 'user0001com'}
            ).find('a').attrs['href'],
        )

        #   Make sure we *don't* have an alert summary heading
        self.assertEquals(
            response.html.find(
                'h3',
                attrs={'class': 'alert-summary-heading'}
            ).text,
            'Please add additional information'
        )

    #   Check that a link showing the user's slug appears in the top nav
    #   bar
    def test_slug_and_link_exists_in_nav(self):
        #   Create the user
        User(slug='user0001com', original_slug='user@0001.com').save()

        #   Log in as user
        form = self.app.get(reverse('login-view')).form
        form['slug'] = 'user0001com'
        response = form.submit()

        #   Go to the profile page (any page would do)
        response = self.app.get(
            reverse(
                'user-detail',
                kwargs={'slug': 'user0001com'}
            )
        )

        #   Check that the slug is displayed at the top, that it has a link
        #   and the link test is the user's slug
        slug_div = response.html.find(
                    'span',
                    attrs={'data-slug': 'user0001com'}
                )
        self.assertTrue(slug_div)
        slug_link = slug_div.find('a')
        self.assertTrue(slug_link)
        slug_text = slug_link.text
        self.assertIn('user@0001.com', slug_text)

    #   Check that a link showing the user's username appears in the top nav
    #   bar
    def test_username_and_link_exists_in_nav(self):
        #   Create the user
        User(
            slug='user0001com',
            original_slug='user@0001.com',
            username='User 0001'
        ).save()

        #   Log in as user
        form = self.app.get(reverse('login-view')).form
        form['slug'] = 'user0001com'
        response = form.submit()

        #   Go to the profile page (any page would do)
        response = self.app.get(
            reverse(
                'user-detail',
                kwargs={'slug': 'user0001com'}
            )
        )
        #   Check that the username is displayed at the top, that it has a link
        #   and the link test is the user's slug
        slug_div = response.html.find(
                    'span',
                    attrs={'data-slug': 'user0001com'}
                )
        self.assertTrue(slug_div)
        slug_link = slug_div.find('a')
        self.assertTrue(slug_link)
        slug_text = slug_link.text
        self.assertIn('User 0001', slug_text)
