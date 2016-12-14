# (c) Crown Owned Copyright, 2016. Dstl.

from django.core.urlresolvers import reverse
from django_webtest import WebTest


class KeycloakHeaderLandAtHome(WebTest):
    def test_auto_login_on_landing(self):
        headers = {'KEYCLOAK_USERNAME': 'user@0001.com'}
        response = self.app.get(reverse('home'), headers=headers)
        self.assertEqual('http://localhost:80/links', response.location)
