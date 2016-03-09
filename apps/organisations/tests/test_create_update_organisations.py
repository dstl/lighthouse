# (c) Crown Owned Copyright, 2016. Dstl.
from django.core.urlresolvers import reverse
from django_webtest import WebTest
import re

from apps.organisations.models import Organisation


class OrganisationCreateWebTest(WebTest):
    def test_cannot_create_nameless_organisation(self):
        form = self.app.get(reverse('organisation-create')).form
        response = form.submit()
        form = response.context['form']
        self.assertIn(
            'This field is required.',
            form['name'].errors
        )

    def test_create_new_organisation_from_list_view(self):
        form = self.app.get(reverse('organisation-list')).form
        form['name'] = 'org0001'
        response = form.submit()
        self.assertEquals(response.status_int, 302)

        response = self.app.get(reverse('organisation-list'))
        response = self.app.get(response.html.find(
                'a',
                text=re.compile(r'org0001')
            ).attrs['href']
        )
        org_name = response.html.find(
            'h1',
            attrs={'class': 'heading-xlarge'}
        ).text
        self.assertEquals(org_name, 'Organisation: org0001')

    def test_cannot_create_duplicate_organisation(self):
        o = Organisation(name='alpha')
        o.save()
        form = self.app.get(reverse('organisation-list')).form
        form['name'] = 'alpha'
        response = form.submit()
        form = response.context['form']
        self.assertIn(
            'Organisation with this Name already exists.',
            form['name'].errors
        )
