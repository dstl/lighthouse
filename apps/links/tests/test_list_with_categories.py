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
        self.assertIsNotNone(mappingLbl)
        self.assertIsNotNone(filterEl.find(id='categories-filter-mapping'))

        socialLbl = filterEl.find(attrs={'for': 'categories-filter-social'})
        self.assertIsNotNone(socialLbl)
        self.assertIsNotNone(filterEl.find(id='categories-filter-social'))

        geoLbl = filterEl.find(attrs={'for': 'categories-filter-geospatial'})
        self.assertIsNotNone(geoLbl)
        self.assertIsNotNone(filterEl.find(id='categories-filter-geospatial'))

        imageryLbl = filterEl.find(attrs={'for': 'categories-filter-imagery'})
        self.assertIsNotNone(imageryLbl)
        self.assertIsNotNone(filterEl.find(id='categories-filter-imagery'))

        assert 'Mapping' in mappingLbl.text
        assert 'Social' in socialLbl.text
        assert 'Geospatial' in geoLbl.text
        assert 'Imagery' in imageryLbl.text

    def test_filter_by_single_category(self):
        response = self.app.get(reverse('link-list'))

        form = response.form

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
            self.el3.name
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
