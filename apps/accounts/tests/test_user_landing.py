# (c) Crown Owned Copyright, 2016. Dstl.

from django.core.urlresolvers import reverse

from django_webtest import WebTest

class KeycloakHeaderLandAtHome(WebTest):
    def test_auto_login(self):
        headers = { 'KEYCLOAK_USERNAME' : 'user@0001.com' }
        response = self.app.get(reverse('home'), headers=headers)
        self.assertEqual(reverse('link-list'), response.location)

