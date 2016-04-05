# (c) Crown Owned Copyright, 2016. Dstl.

from django.core.urlresolvers import reverse

from django_webtest import WebTest

from apps.organisations.models import Organisation
from apps.teams.models import Team
from apps.users.models import User
from testing.common import login_user


class TeamWebTest(WebTest):
    def test_join_button_visible(self):
        #   Create an organisation, a team and a user and assign that
        #   team to that user.
        o = Organisation(name="org0001")
        o.save()
        t = Team(name="team0001", organisation=o)
        t.save()
        User(slug='user0001com', original_slug='user@0001.com').save()
        # u.teams.add(t).save()

        #   Now we need to log in as that user.
        form = self.app.get(reverse('login-view')).form
        form['slug'] = 'user0001com'
        form.submit().follow()

        #   Now go visit the team page...
        response = self.app.get(
            reverse(
                'team-detail',
                kwargs={'pk': t.pk}
            )
        )

        form = response.form

        self.assertEqual(
            form.method,
            'post'
        )

        self.assertEqual(
            form.action,
            '/teams/' + str(t.pk) + '/join'
        )

        # Make sure this button no longer exists
        self.assertIsNone(
            response.html.find(
                'a',
                attrs={'href': '/teams/' + str(t.pk) + '/leave'}
            )
        )
        # Make sure this button no longer exists
        self.assertIsNone(
            response.html.find(
                'a',
                attrs={'href': '/teams/' + str(t.pk) + '/join'}
            )
        )

    def test_leave_button_visible(self):
        #   Create an organisation, a team and a user and assign that
        #   team to that user.
        o = Organisation(name="org0001")
        o.save()
        t = Team(name="team0001", organisation=o)
        t.save()
        u = User(slug='user0001com', original_slug='user@0001.com')
        u.save()
        u.teams.add(t)
        u.save()

        #   Now we need to log in as that user.
        form = self.app.get(reverse('login-view')).form
        form['slug'] = 'user0001com'
        form.submit().follow()

        #   Now go visit the team page...
        response = self.app.get(
            reverse(
                'team-detail',
                kwargs={'pk': t.pk}
            )
        )

        form = response.form

        self.assertEqual(
            form.method,
            'post'
        )

        self.assertEqual(
            form.action,
            '/teams/' + str(t.pk) + '/leave'
        )

        # Make sure this button no longer exists
        self.assertIsNone(
            response.html.find(
                'a',
                attrs={'href': '/teams/' + str(t.pk) + '/leave'}
            )
        )
        # Make sure this button no longer exists
        self.assertIsNone(
            response.html.find(
                'a',
                attrs={'href': '/teams/' + str(t.pk) + '/join'}
            )
        )

    def test_join_leave_buttons_work(self):
        #   Create an organisation, a team and a user and assign that
        #   team to that user.
        o = Organisation(name="org0001")
        o.save()
        t = Team(name="team0001", organisation=o)
        t.save()
        u = User(slug='user0001com', original_slug='user@0001.com')
        u.save()

        login_user(self, u)

        response = self.app.get(
            reverse(
                'team-detail',
                kwargs={'pk': t.pk}
            )
        )

        form = response.form

        self.assertEqual(
            form.method,
            'post'
        )

        self.assertEqual(
            form.action,
            '/teams/' + str(t.pk) + '/join'
        )

        response = form.submit().follow()

        # Make sure the user is now in the team
        response = self.app.get(
            reverse(
                'user-detail',
                kwargs={'slug': u.slug}
            )
        )

        self.assertTrue(
            response.html.find(
                'a',
                attrs={
                    'class': 'main-list-item',
                    'href': '/teams/' + str(t.pk)
                }
            )
        )

        # Go back to the team detail page so we can submit the link
        response = self.app.get(
            reverse(
                'team-detail',
                kwargs={'pk': t.pk}
            )
        )

        form = response.form

        self.assertEqual(
            form.method,
            'post'
        )

        self.assertEqual(
            form.action,
            '/teams/' + str(t.pk) + '/leave'
        )

        response = form.submit().follow()

        # Make sure the user is no longer in the team
        response = self.app.get(
            reverse(
                'user-detail',
                kwargs={'slug': u.slug}
            )
        )
        self.assertFalse(
            response.html.find(
                'a',
                attrs={
                    'class': 'main-list-item',
                    'href': '/teams/' + str(t.pk)
                }
            )
        )
