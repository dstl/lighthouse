from django.core.urlresolvers import reverse
from django_webtest import WebTest
from apps.users.models import User


class LoginTest(WebTest):

    def test_login_view_no_users(self):
        response = self.app.get(reverse('login-view'))

        self.assertEquals(0, len(response.context['users']))
        self.assertEquals(response.status_int, 200)

    def test_login_view(self):
        u1 = User(
            fullName='John Smith',
            phone='0 123 4567 890',
            email='john.smith@smithmail.com',
        )
        u1.save()

        response = self.app.get(reverse('login-view'))
        self.assertEquals(response.status_int, 200)
        self.assertIn(u1, response.context['users'])

        self.assertIn('John Smith', response)
