from django.core.urlresolvers import reverse

from django_webtest import WebTest


class LinkTest(WebTest):
    def test_create_link(self):
        form = self.app.get(reverse('link-create')).form
        form['name'] = 'Google'
        form['destination'] = 'https://google.com'
        response = form.submit().follow()
        response.mustcontain('<h1>Google</h1>')
