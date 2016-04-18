# (c) Crown Owned Copyright, 2016. Dstl.


from django.test import TestCase

from apps.links.models import Link
from testing.common import generate_fake_links, make_user


class LinkModelTest(TestCase):
    def test_lighthouse_has_first_links(self):
        """
        Ensure that the migrations responsible for the creation of the
        Lighthouse links have captured the first two links
        """
        user = make_user()
        (l1, l2) = generate_fake_links(owner=user, count=2)

        all_links = Link.objects.all()
        self.assertEqual(len(all_links), 4)

        lighthouse = Link.objects.get(pk=1)
        self.assertEqual(lighthouse.name, 'Lighthouse')
        self.assertEqual(lighthouse.destination, '/')
        self.assertEqual(
            lighthouse.description,
            'Web application for finding useful tools, data and techniques'
        )

        lighthouse_api = Link.objects.get(pk=2)
        self.assertEqual(lighthouse_api.name, 'Lighthouse API')
        self.assertEqual(lighthouse_api.destination, '/api/')
        self.assertEqual(
            lighthouse_api.description,
            'The API for this application.'
        )
