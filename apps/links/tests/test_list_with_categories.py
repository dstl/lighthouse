# (c) Crown Owned Copyright, 2016. Dstl.
from django.core.urlresolvers import reverse
from .common import generate_fake_links, make_user, login_user

from django_webtest import WebTest


class ListLinksWithCategoriesTest(WebTest):
    def setUp(self):
        self.logged_in_user = make_user()

        (self.el1, self.el2, self.el3,
            self.el4, self.el5, self.el6) = generate_fake_links(
            self.logged_in_user,
            count=6
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

        self.assertTrue(login_user(self, self.logged_in_user))

    def test_all_categories_appear(self):
        response = self.app.get(reverse('link-list'))

        # They should appear with the newest one at the top by the default
        # sorting method

        filterEl = response.html.find(id='categories-filter')

        mappingLbl = filterEl.find(attrs={'for': 'categories-filter-mapping'})
        mappingCheckbox = filterEl.find(id='categories-filter-mapping')
        self.assertIsNotNone(mappingLbl)
        self.assertIsNotNone(mappingCheckbox)
        self.assertEquals(mappingCheckbox.attrs['value'], 'mapping')
        self.assertFalse('checked' in mappingCheckbox.attrs)

        socialLbl = filterEl.find(attrs={'for': 'categories-filter-social'})
        socialCheckbox = filterEl.find(id='categories-filter-social')
        self.assertIsNotNone(socialLbl)
        self.assertIsNotNone(socialCheckbox)
        self.assertEquals(socialCheckbox.attrs['value'], 'social')
        self.assertFalse('checked' in socialCheckbox.attrs)

        geoLbl = filterEl.find(attrs={'for': 'categories-filter-geospatial'})
        geoCheckbox = filterEl.find(id='categories-filter-geospatial')
        self.assertIsNotNone(geoLbl)
        self.assertIsNotNone(geoCheckbox)
        self.assertEquals(geoCheckbox.attrs['value'], 'geospatial')
        self.assertFalse('checked' in geoCheckbox.attrs)

        imageryLbl = filterEl.find(attrs={'for': 'categories-filter-imagery'})
        imageryCheckbox = filterEl.find(id='categories-filter-imagery')
        self.assertIsNotNone(imageryLbl)
        self.assertIsNotNone(imageryCheckbox)
        self.assertEquals(imageryCheckbox.attrs['value'], 'imagery')
        self.assertFalse('checked' in imageryCheckbox.attrs)

        assert 'Mapping' in mappingLbl.text
        assert 'Social' in socialLbl.text
        assert 'Geospatial' in geoLbl.text
        assert 'Imagery' in imageryLbl.text

    def test_filter_by_single_category(self):

        response = self.app.get(reverse('link-list'))

        form = response.form

        self.assertEquals(
            form.get('categories', index=0).id, 'categories-filter-mapping'
        )
        form.get('categories', index=0).checked = True

        response = form.submit()
        form = response.form

        self.assertEquals(
            len(response.html.findAll('li', {'class': 'link-list-item'})),
            3
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
            self.el2.name,
            response.html.findAll(
                'li',
                {'class': 'link-list-item'}
            )[1].text,
        )

        self.assertIn(
            self.el1.name,
            response.html.findAll(
                'li',
                {'class': 'link-list-item'}
            )[2].text,
        )

        self.assertTrue(form.get('categories', index=0).checked)

    def test_filter_by_multiple_categories(self):

        response = self.app.get(reverse('link-list'))

        form = response.form

        self.assertEquals(
            form.get('categories', index=0).id, 'categories-filter-mapping'
        )
        form.get('categories', index=0).checked = True

        self.assertEquals(
            form.get('categories', index=2).id, 'categories-filter-geospatial'
        )
        form.get('categories', index=2).checked = True

        response = form.submit()
        form = response.form

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
            self.el4.name,
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

        self.assertTrue(form.get('categories', index=0).checked)
        self.assertTrue(form.get('categories', index=2).checked)
