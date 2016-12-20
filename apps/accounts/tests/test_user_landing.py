# (c) Crown Owned Copyright, 2016. Dstl.

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django_webtest import WebTest

from apps.teams.models import Team
from apps.organisations.models import Organisation


class KeycloakHeaderLandAtHome(WebTest):
    def test_auto_login_on_landing(self):
        headers = {'KEYCLOAK_USERNAME': 'user@0001.com'}
        first_step = self.app.get(reverse('home'), headers=headers)
        self.assertEqual('http://localhost:80/login', first_step.location)

        second_response = self.app.get(first_step.location, headers=headers)
        self.assertEqual(
            'http://localhost:80/users/user0001com/update-profile',
            second_response.location
        )

    def test_auto_login_on_landing_for_full_profile(self):
        o = Organisation(name='org0001')
        o.save()
        t = Team(name='team0001', organisation=o)
        t.save()

        user = get_user_model().objects.create_user(
            userid='user@0001.com',
            name='User 0001',
            best_way_to_find='In the kitchen',
            best_way_to_contact='By email',
            phone='00000000',
            email='user@0001.com',
        )
        user.teams.add(t)
        user.save()

        headers = {'KEYCLOAK_USERNAME': 'user@0001.com'}
        first_step = self.app.get(reverse('home'), headers=headers)
        self.assertEqual('http://localhost:80/login', first_step.location)

        second_response = self.app.get(first_step.location, headers=headers)
        self.assertEqual(
            'http://localhost:80/links',
            second_response.location
        )
