# (c) Crown Owned Copyright, 2016. Dstl.
# apps/organisations/tests.py
from django.core.urlresolvers import reverse
from django_webtest import WebTest
from django.test import TestCase
from django.db.utils import IntegrityError

from .models import Organisation


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
