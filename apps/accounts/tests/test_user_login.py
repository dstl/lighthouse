# (c) Crown Owned Copyright, 2016. Dstl.


from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse

from django_webtest import WebTest

from apps.teams.models import Team
from apps.organisations.models import Organisation


class UserWebTest(WebTest):
    def test_can_login(self):
        get_user_model().objects.create_user(userid='user@0001.com')

        form = self.app.get(reverse('login')).form
        form['userid'] = 'user@0001.com'
        response = form.submit().follow()

        # userid in the navigation, login link not
        self.assertTrue(
            response.html.find(
                'span',
                attrs={'data-slug': 'user0001com'}
            )
        )
        self.assertFalse(
            response.html.find('a', class_='login')
        )

    def test_new_userid_creates_normal_account(self):
        form = self.app.get(reverse('login')).form
        form['userid'] = 'user@0001.com'
        response = form.submit().follow()

        # userid in the navigation, login link not
        self.assertTrue(
            response.html.find(
                'span',
                attrs={'data-slug': 'user0001com'}
            )
        )
        self.assertFalse(
            response.html.find('a', class_='login')
        )

        # created a passwordless user in the db
        user = get_user_model().objects.get(slug='user0001com')
        self.assertTrue(user.pk)
        self.assertFalse(user.has_usable_password())

    def test_no_userid_doesnt_create_account(self):
        form = self.app.get(reverse('login')).form
        response = form.submit()

        # login link in the navigation
        self.assertTrue(
            response.html.find('a', class_='login')
        )

    def test_login_as_user_with_password_redirects_to_admin(self):
        get_user_model().objects.create_user(
            userid='user@0001.com', password='password')

        form = self.app.get(reverse('login')).form
        form['userid'] = 'user@0001.com'
        response = form.submit()
        self.assertEquals(response.status_code, 302)
        self.assertEquals(response.location, 'http://localhost:80/admin/')

    #   We want to test that a user who is missing a username is redirected
    #   to the update user profile page
    def test_user_missing_data_redirected(self):
        #   This user doesn't have a username
        user = get_user_model().objects.create_user(userid='user@0001.com')

        #   Log in as user
        form = self.app.get(reverse('login')).form
        form['userid'] = 'user@0001.com'
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
                'span', attrs={'data-slug': user.slug}
            ).find('a').attrs['href'],
            '/users/' + str(user.slug) + '/update-profile'
        )

        #   We should now be on the user needs to add information page
        self.assertEquals(
            response.html.find(
                'h3',
                attrs={'class': 'error-summary-heading'}
            ).text,
            'Please add your name'
        )

    #   Meanwhile a user who has a username but no teams will end up
    #   at the page asking for them to enter additional team information
    def test_user_has_username_but_no_teams_redirected(self):
        #   This user has a username
        user = get_user_model().objects.create_user(
            userid='user@0001.com', name='User 0001')

        #   Log in as user
        form = self.app.get(reverse('login')).form
        form['userid'] = 'user@0001.com'
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
                'span', attrs={'data-slug': user.slug}
            ).find('a').attrs['href'],
            '/users/' + str(user.slug) + '/update-profile/teams'
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

        user = get_user_model().objects.create_user(
            userid='user@0001.com', name='User 0001')
        user.teams.add(t)
        user.save()

        #   Log in as user
        form = self.app.get(reverse('login')).form
        form['userid'] = 'user@0001.com'
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
        get_user_model().objects.create_user(userid='user@0001.com')

        #   Log in as user
        form = self.app.get(reverse('login')).form
        form['userid'] = 'user@0001.com'
        response = form.submit().follow()

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
        get_user_model().objects.create_user(
            userid='user@0001.com', name='User 0001')

        #   Log in as user
        form = self.app.get(reverse('login')).form
        form['userid'] = 'user@0001.com'
        response = form.submit().follow()

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


class KeycloakHeaderLoginTest(WebTest):
    def test_auto_login(self):
        headers = { 'KEYCLOAK_USERNAME' : 'user@0001.com' }
        response = self.app.get(reverse('login'), headers=headers)
        self.assertEqual(
            'http://localhost:80/users/user0001com/update-profile',
            response.location
        )

    def test_auto_login_for_admin(self):
        get_user_model().objects.create_user(
            userid='admin@0001.com', password='password')
        
        headers = { 'KEYCLOAK_USERNAME' : 'admin@0001.com' }
        response = self.app.get(reverse('login'), headers=headers)
        self.assertEqual(
            'http://localhost:80/users/admin0001com/update-profile',
            response.location
        )