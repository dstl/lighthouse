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

        exp = 'The API for this application.\n\n'
        exp += 'Documentation for using the API can '
        exp += 'be found at [/api/](/api/).'

        self.assertEqual(
            lighthouse_api.description,
            exp
        )

    def test_description_summary_with_markdown(self):
        user = make_user()
        desc = '* A summary is something that summarises something longer'
        desc += '\n* Summaries are really useful'
        desc += '\n\n## Header 1'
        link = Link.objects.create(
            name='Markdown',
            description=desc,
            owner=user)

        expected = 'A summary is something that summarises something longer'

        self.assertEqual(
            link.description_summary,
            expected
        )

    def test_description_summary_with_very_long_line(self):
        user = make_user()
        desc = '* A summary is something that summarises something longer'
        desc += ' than what it is meant to be. Something very, very long might'
        desc += ' want to be shortened to make it easier to read in a list,'
        desc += ' for example.'
        desc += '\n\n## Header 1'

        link = Link.objects.create(
            name='Markdown',
            description=desc,
            owner=user)

        expected = 'A summary is something that summarises something longer'
        expected += ' than what it is meant to be. Something very, very long'
        expected += ' might want to be shortened to...'

        self.assertEqual(
            link.description_summary,
            expected
        )
