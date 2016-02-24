from django.core.urlresolvers import reverse
from django_webtest import WebTest
from django.test import TestCase
from django.db.utils import IntegrityError

from .models import Organisation


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


class OrganisationTest(TestCase):
    def setUp(self):
        o = Organisation(name='Existing Org')
        o.save()

    def test_cannot_add_nameless_organisation(self):
        # FIXME write the damn test
        pass

    def test_can_create_organisation(self):
        o = Organisation(name='testy')
        o.save()
        self.assertTrue(o.pk)

    def test_cannot_create_duplicate_organisations(self):
        o = Organisation(name='New Org')
        o.save()
        self.assertTrue(o.pk)
        o = Organisation(name='Existing Org')
        with self.assertRaises(IntegrityError):
            o.save()


class OrganisationWebTest(WebTest):
    def test_cannot_create_nameless_organisation(self):
        form = self.app.get(reverse('organisation-create')).form
        response = form.submit()
        form = response.context['form']
        self.assertIn(
            'This field is required.',
            form['name'].errors
        )
