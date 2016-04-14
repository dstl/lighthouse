# (c) Crown Owned Copyright, 2016. Dstl.


from django.test import TestCase

from apps.links.models import Link
from testing.common import generate_fake_links, make_user


class LinkModelTest(TestCase):
    def test_lighthouse_is_first_link(self):
        """
        Test that the migration scripts responsible for the creation of the
        Lighthouse link and default user
        """
        user = make_user()
        (l1, l2) = generate_fake_links(owner=user, count=2)

        first_link = Link.objects.get(pk=1)

        all_links = Link.objects.all()

        description = 'Web application for finding useful'
        description += ' tools, data and techniques'

        self.assertEqual(first_link.name, 'Lighthouse')
        self.assertEqual(first_link.description, description)
        self.assertEqual(first_link.destination, '/')
        self.assertEqual(first_link.pk, 1)
        self.assertEqual(len(all_links), 3)

        self.assertEqual(first_link.owner.name, 'Lighthouse User')
