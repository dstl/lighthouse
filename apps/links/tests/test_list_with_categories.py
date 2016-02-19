from django.core.urlresolvers import reverse
from apps.users.models import User
from apps.links.models import Link
from .common import generate_fake_links

from django_webtest import WebTest


class ListLinksWithCategoriesTest(WebTest):
    def setUp(self):
        self.logged_in_user = User(
            fullName='Fake Fakerly',
            phone='555-2187',
            email='fake@dstl.gov.uk')
        self.logged_in_user.save()

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

        response = self.app.get(reverse('login-view'))

        response = response.click('Fake Fakerly').follow()

        self.assertEquals(response.html.h1.text, 'Fake Fakerly')

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

        self.assertEquals(
            len(response.html.findAll('li', {'class': 'link-list-item'})),
            3
        )

        self.assertIsNone(response.html.find('ol', {'class': 'pagination'}))

        self.assertEquals(
            response.html.findAll(
                'li',
                {'class': 'link-list-item'}
            )[0].text,
            self.el6.name
        )

        self.assertEquals(
            response.html.findAll(
                'li',
                {'class': 'link-list-item'}
            )[1].text,
            self.el2.name
        )

        self.assertEquals(
            response.html.findAll(
                'li',
                {'class': 'link-list-item'}
            )[2].text,
            self.el1.name
        )
        # Check that only the appropriate links are on the page
        # Check that the pagination reflects the smaller result set
