from django.core.urlresolvers import reverse
from .models import Link

from django_webtest import WebTest

import pdb


class LinkTest(WebTest):
    def test_create_link(self):
        form = self.app.get(reverse('link-create')).form
        form['name'] = 'Google'
        form['destination'] = 'https://google.com'
        response = form.submit().follow()
        response.mustcontain('<h1>Google</h1>')

    def test_edit_link(self):
        existing_link = Link(
            name='Wikimapia',
            description='A great mapping application',
            destination='https://wikimapia.org')
        existing_link.save()

        form = self.app.get(
            reverse('link-edit', kwargs={'pk': existing_link.pk})).form

        # pdb.set_trace()

        self.assertEquals(form['name'].value, 'Wikimapia')
        self.assertEquals(form['description'].value,
                          'A great mapping application')
        self.assertEquals(form['destination'].value, 'https://wikimapia.org')
