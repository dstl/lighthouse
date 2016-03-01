# (c) Crown Owned Copyright, 2016. Dstl.
# apps/users/tests.py
from django.core.urlresolvers import reverse
from django_webtest import WebTest


class UserTest(WebTest):

    def test_create_a_user_success(self):
        form = self.app.get(reverse('user-create')).form
        form['fullName'] = 'Jane Smith'
        form['phone'] = '0 123 4567 890'
        form['email'] = 'jane.smith@smithmail.com'

        response = form.submit().follow()

        self.assertEquals(response.status_int, 200)

        user = response.context['user']

        self.assertEquals(user.fullName, 'Jane Smith')
        self.assertEquals(user.phone, '0 123 4567 890')
        self.assertEquals(user.email, 'jane.smith@smithmail.com')

    def test_create_minimal_user(self):
        form = self.app.get(reverse('user-create')).form
        form['fullName'] = 'Jane Smith'

        response = form.submit().follow()
        user = response.context['user']

        self.assertEquals(user.fullName, 'Jane Smith')
        self.assertEquals(user.phone, '')
        self.assertEquals(user.email, '')

    def test_create_a_user_fail(self):
        form = self.app.get(reverse('user-create')).form
        form['fullName'] = ''
        form['phone'] = ''
        form['email'] = ''

        response = form.submit()
        form = response.context['form']
        self.assertIn(
            "This field is required.",
            form['fullName'].errors
        )
