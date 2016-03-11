# (c) Crown Owned Copyright, 2016. Dstl.

from datetime import datetime
from unittest import mock

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client
from django.utils.timezone import make_aware

from ..models import Link
from .common import make_user


class LinkUsageAPITest(TestCase):
    def setUp(self):
        self.user = make_user()
        self.link = Link.objects.create(
            name='Link Linkerly',
            destination='link.com',
            owner=self.user,
            is_external=False,
        )

    def test_get_usage(self):
        with mock.patch('django.utils.timezone.now') as mock_now:
            # register usage on a specific day
            mock_now.return_value = make_aware(datetime(2016, 3, 1, 10, 0, 0))
            self.link.register_usage(self.user)

        expected_response = [{
            'date': '2016-03-01T10:00:00Z',
            'user': self.user.slug,
        }]

        c = Client()
        response = c.get(
            reverse('api-link-usage', kwargs={'pk': self.link.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode('utf8'),
            expected_response
        )

    def test_cannot_update_usage_without_user(self):
        self.assertEquals(self.link.usage_total(), 0)

        c = Client()
        response = c.post(
            reverse('api-link-usage', kwargs={'pk': self.link.pk}),
            {}
        )

        self.assertEqual(response.status_code, 400)
        self.assertEquals(self.link.usage_total(), 0)

    def test_cannot_update_usage_with_invalid_user(self):
        self.assertEquals(self.link.usage_total(), 0)

        c = Client()
        response = c.post(
            reverse('api-link-usage', kwargs={'pk': self.link.pk}),
            {'user': 'the-easter-bunny'}
        )

        self.assertEqual(response.status_code, 400)
        self.assertEquals(self.link.usage_total(), 0)

    def test_update_usage(self):
        self.assertEquals(self.link.usage_total(), 0)

        c = Client()
        response = c.post(
            reverse('api-link-usage', kwargs={'pk': self.link.pk}),
            {'user': self.user.slug}
        )

        self.assertEqual(response.status_code, 201)
        self.assertEquals(self.link.usage_total(), 1)
