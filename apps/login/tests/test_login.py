from django.core.urlresolvers import reverse
from django_webtest import WebTest


class LoginTest(WebTest):

    def test_login_view(self):
        response = self.app.get(reverse('login-view'))
        self.assertEquals(response.status_int, 200)
