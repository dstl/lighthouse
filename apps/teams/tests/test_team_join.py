# (c) Crown Owned Copyright, 2016. Dstl.
# apps/teams/tests.py
from django.core.urlresolvers import reverse
from django_webtest import WebTest
from apps.teams.models import Team
from apps.organisations.models import Organisation
from apps.users.models import User


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
        #   ...and see if the "join" button appears...
        self.assertTrue(
            response.html.find(
                'a',
                attrs={'href': '/teams/' + str(t.pk) + '/join'}
            )
        )
        #   ...and that the "leave" button doesn't...
        self.assertFalse(
            response.html.find(
                'a',
                attrs={'href': '/teams/' + str(t.pk) + '/leave'}
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
        #   ...and see if the "leave" button appears...
        self.assertTrue(
            response.html.find(
                'a',
                attrs={'href': '/teams/' + str(t.pk) + '/leave'}
            )
        )
        #   ...and that the "join" button doesn't...
        self.assertFalse(
            response.html.find(
                'a',
                attrs={'href': '/teams/' + str(t.pk) + '/join'}
            )
        )

    def test_join_leave_link_works(self):
        #   Create an organisation, a team and a user and assign that
        #   team to that user.
        o = Organisation(name="org0001")
        o.save()
        t = Team(name="team0001", organisation=o)
        t.save()
        u = User(slug='user0001com', original_slug='user@0001.com')
        u.save()

        #   Now we need to log in as that user.
        form = self.app.get(reverse('login-view')).form
        form['slug'] = 'user0001com'
        form.submit().follow()

        #   Assert that a link to the team doesn't exists (because we are
        #   not a member of it yet.)
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

        #   Now go visit the join url
        self.app.get(
            reverse(
                'team-join',
                kwargs={'pk': t.pk}
            )
        )

        #   Now go to the user's profile and see if a link to the team exists
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

        #   Now go visit the leave url
        self.app.get(
            reverse(
                'team-leave',
                kwargs={'pk': t.pk}
            )
        )

        #   And once again check the link to the team has gone
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
