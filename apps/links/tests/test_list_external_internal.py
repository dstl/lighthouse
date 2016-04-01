# (c) Crown Owned Copyright, 2016. Dstl.

from django.core.urlresolvers import reverse

from django_webtest import WebTest

from testing.common import generate_fake_links, login_user, make_user


class ListLinksWithExternalityTest(WebTest):
    def setUp(self):
        self.logged_in_user = make_user()

        self.el1, self.el2, self.el3 = generate_fake_links(
            self.logged_in_user,
            count=3,
            is_external=True
        )

        self.el4, self.el5 = generate_fake_links(
            self.logged_in_user,
            start=4,
            count=2
        )

        # Note: the generator expects to send out a tuple, so allow that.
        (self.el6,) = generate_fake_links(
            self.logged_in_user,
            start=6,
            count=1,
            is_external=True
        )

        (self.el7,) = generate_fake_links(
            self.logged_in_user,
            start=7,
            count=1
        )

        self.el1.categories.add('mapping')
        self.el1.categories.add('social')
        self.el1.save()

        self.el2.categories.add('mapping')
        self.el2.save()

        self.el3.categories.add('social')
        self.el3.save()

        self.el4.categories.add('geospatial')
        self.el4.save()

        self.el5.categories.add('imagery')
        self.el5.save()

        self.el6.categories.add('geospatial')
        self.el6.categories.add('mapping')
        self.el6.save()

        self.el7.categories.add('social')
        self.el7.categories.add('mapping')
        self.el7.save()

        self.assertTrue(login_user(self, self.logged_in_user))

    def test_external_internal_printed(self):
        response = self.app.get(reverse('link-list'))

        self.assertIn(
            self.el7.name,
            response.html.findAll(
                'li',
                {'class': 'link-list-item'}
            )[0].text,
        )

        self.assertIn(
            'Internal',
            response.html.findAll(
                'li',
                {'class': 'link-list-item'}
            )[0].text,
        )

        self.assertIn(
            self.el6.name,
            response.html.findAll(
                'li',
                {'class': 'link-list-item'}
            )[1].text,
        )

        self.assertIn(
            'External',
            response.html.findAll(
                'li',
                {'class': 'link-list-item'}
            )[1].text,
        )

    def test_external_internal_checkboxes(self):
        response = self.app.get(reverse('link-list'))

        filterEl = response.html.find(id='categories-filter')

        externalLbl = filterEl.find(attrs={'for': 'types-filter-external'})
        externalCheckbox = filterEl.find(id='types-filter-external')
        self.assertIsNotNone(externalLbl)
        self.assertIsNotNone(externalCheckbox)
        self.assertEquals(externalCheckbox.attrs['value'], 'external')
        self.assertFalse('checked' in externalCheckbox.attrs)

        internalLbl = filterEl.find(attrs={'for': 'types-filter-internal'})
        internalCheckbox = filterEl.find(id='types-filter-internal')
        self.assertIsNotNone(internalLbl)
        self.assertIsNotNone(internalCheckbox)
        self.assertEquals(internalCheckbox.attrs['value'], 'internal')
        self.assertFalse('checked' in internalCheckbox.attrs)

    def test_external_checkboxes_filter(self):
        response = self.app.get(reverse('link-list'))

        form = response.forms['list-results']

        self.assertEquals(
            form.get('types', index=0).id, 'types-filter-external'
        )
        form.get('types', index=0).checked = True

        response = form.submit()
        form = response.forms['list-results']

        self.assertEquals(
            len(response.html.findAll('li', {'class': 'link-list-item'})),
            4
        )

        self.assertIsNone(response.html.find('ol', {'class': 'pagination'}))

        self.assertIn(
            self.el6.name,
            response.html.findAll(
                'li',
                {'class': 'link-list-item'}
            )[0].text,
        )

        self.assertIn(
            self.el3.name,
            response.html.findAll(
                'li',
                {'class': 'link-list-item'}
            )[1].text,
        )

        self.assertIn(
            self.el2.name,
            response.html.findAll(
                'li',
                {'class': 'link-list-item'}
            )[2].text,
        )

        self.assertIn(
            self.el1.name,
            response.html.findAll(
                'li',
                {'class': 'link-list-item'}
            )[3].text,
        )

        self.assertTrue(form.get('types', index=0).checked)
        self.assertFalse(form.get('types', index=1).checked)

    def test_internal_checkboxes_filter(self):
        response = self.app.get(reverse('link-list'))

        form = response.forms['list-results']

        self.assertEquals(
            form.get('types', index=1).id, 'types-filter-internal'
        )
        form.get('types', index=1).checked = True

        response = form.submit()
        form = response.forms['list-results']

        self.assertEquals(
            len(response.html.findAll('li', {'class': 'link-list-item'})),
            3
        )

        self.assertIsNone(response.html.find('ol', {'class': 'pagination'}))

        self.assertIn(
            self.el7.name,
            response.html.findAll(
                'li',
                {'class': 'link-list-item'}
            )[0].text,
        )

        self.assertIn(
            self.el5.name,
            response.html.findAll(
                'li',
                {'class': 'link-list-item'}
            )[1].text,
        )

        self.assertIn(
            self.el4.name,
            response.html.findAll(
                'li',
                {'class': 'link-list-item'}
            )[2].text,
        )

        self.assertFalse(form.get('types', index=0).checked)
        self.assertTrue(form.get('types', index=1).checked)

    def test_internal_and_external_checkboxes_filter(self):
        response = self.app.get(reverse('link-list'))

        form = response.forms['list-results']

        self.assertEquals(
            form.get('types', index=0).id, 'types-filter-external'
        )
        form.get('types', index=0).checked = True

        self.assertEquals(
            form.get('types', index=1).id, 'types-filter-internal'
        )
        form.get('types', index=1).checked = True

        response = form.submit()
        form = response.forms['list-results']

        self.assertEquals(
            len(response.html.findAll('li', {'class': 'link-list-item'})),
            5
        )

        self.assertIsNotNone(response.html.find('ol', {'class': 'pagination'}))

        self.assertIn(
            self.el7.name,
            response.html.findAll(
                'li',
                {'class': 'link-list-item'}
            )[0].text,
        )

        self.assertIn(
            self.el6.name,
            response.html.findAll(
                'li',
                {'class': 'link-list-item'}
            )[1].text,
        )

        self.assertIn(
            self.el5.name,
            response.html.findAll(
                'li',
                {'class': 'link-list-item'}
            )[2].text,
        )

        self.assertIn(
            self.el4.name,
            response.html.findAll(
                'li',
                {'class': 'link-list-item'}
            )[3].text,
        )

        self.assertIn(
            self.el3.name,
            response.html.findAll(
                'li',
                {'class': 'link-list-item'}
            )[4].text,
        )

        self.assertTrue(form.get('types', index=0).checked)
        self.assertTrue(form.get('types', index=1).checked)
