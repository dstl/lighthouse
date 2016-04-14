# (c) Crown Owned Copyright, 2016. Dstl.

from datetime import datetime
from os import getenv
from unittest import mock, skipIf

import requests

from django.core.urlresolvers import reverse
from django.test import LiveServerTestCase
from django.utils.timezone import make_aware

from ..models import Link
from testing.common import make_user


class LinkUsageAPITest(LiveServerTestCase):
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

            mock_now.return_value = make_aware(datetime(2016, 3, 2, 10, 0, 0))
            self.link.register_usage(self.user)

            mock_now.return_value = make_aware(datetime(2016, 3, 2, 10, 15, 0))
            self.link.register_usage(self.user)

        expected_response = [
            {
                'date': '2016-03-01T10:00:00Z',
                'user': self.user.userid,
                'duration': 0,
            },
            {
                'date': '2016-03-02T10:00:00Z',
                'user': self.user.userid,
                'duration': 900,
            }
        ]
        link_api_url = '%s%s' % (
            self.live_server_url,
            reverse('api-link-usage', kwargs={'pk': self.link.pk}),
        )

        response = requests.get(link_api_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_response)

    def test_cannot_get_invalid_link(self):
        link_api_url = '%s%s' % (
            self.live_server_url,
            reverse('api-link-usage', kwargs={'pk': self.link.pk + 1000}),
        )
        response = requests.get(link_api_url)
        self.assertEqual(response.status_code, 404)

    def test_cannot_update_usage_without_user(self):
        self.assertEquals(self.link.usage_total(), 0)

        expected_response = {'error': 'user required'}
        link_api_url = '%s%s' % (
            self.live_server_url,
            reverse('api-link-usage', kwargs={'pk': self.link.pk}),
        )

        response = requests.post(link_api_url)
        self.assertEqual(response.status_code, 400)
        self.assertEquals(self.link.usage_total(), 0)
        self.assertEquals(response.json(), expected_response)

    def test_cannot_update_usage_with_invalid_user(self):
        self.assertEquals(self.link.usage_total(), 0)

        expected_response = {'error': 'no such user'}
        link_api_url = '%s%s' % (
            self.live_server_url,
            reverse('api-link-usage', kwargs={'pk': self.link.pk}),
        )

        response = requests.post(link_api_url, data={'user': 'easter-bunny'})
        self.assertEqual(response.status_code, 400)
        self.assertEquals(self.link.usage_total(), 0)
        self.assertEquals(response.json(), expected_response)

    def test_update_usage(self):
        self.assertEquals(self.link.usage_total(), 0)

        expected_response = {'status': 'ok'}
        link_api_url = '%s%s' % (
            self.live_server_url,
            reverse('api-link-usage', kwargs={'pk': self.link.pk}),
        )

        response = requests.post(link_api_url, data={'user': self.user.slug})
        self.assertEqual(response.status_code, 201)
        self.assertEquals(self.link.usage_total(), 1)
        self.assertEquals(response.json(), expected_response)

    def test_update_usage_extends_duration(self):
        self.assertEquals(self.link.usage_total(), 0)

        with mock.patch('django.utils.timezone.now') as mock_now:
            # register usage on a specific day
            mock_now.return_value = make_aware(datetime(2016, 3, 1, 10, 0, 0))

            expected_response = {'status': 'ok'}
            link_api_url = '%s%s' % (
                self.live_server_url,
                reverse('api-link-usage', kwargs={'pk': self.link.pk}),
            )

            response = requests.post(
                link_api_url, data={'user': self.user.slug})
            self.assertEqual(response.status_code, 201)
            self.assertEquals(self.link.usage_total(), 1)
            self.assertEquals(response.json(), expected_response)

            # register usage shortly after
            mock_now.return_value = make_aware(datetime(2016, 3, 1, 10, 15, 0))

            expected_response = {'status': 'ok'}
            link_api_url = '%s%s' % (
                self.live_server_url,
                reverse('api-link-usage', kwargs={'pk': self.link.pk}),
            )

            response = requests.post(
                link_api_url, data={'user': self.user.slug})
            self.assertEqual(response.status_code, 201)
            self.assertEquals(self.link.usage_total(), 1)
            self.assertEquals(response.json(), expected_response)

    def test_update_usage_creates_new_usage(self):
        self.assertEquals(self.link.usage_total(), 0)

        with mock.patch('django.utils.timezone.now') as mock_now:
            # register usage on a specific day
            mock_now.return_value = make_aware(datetime(2016, 3, 1, 10, 0, 0))

            expected_response = {'status': 'ok'}
            link_api_url = '%s%s' % (
                self.live_server_url,
                reverse('api-link-usage', kwargs={'pk': self.link.pk}),
            )

            response = requests.post(
                link_api_url, data={'user': self.user.slug})
            self.assertEqual(response.status_code, 201)
            self.assertEquals(self.link.usage_total(), 1)
            self.assertEquals(response.json(), expected_response)

            # register usage after one hour, triggers new usage stat
            mock_now.return_value = make_aware(datetime(2016, 3, 1, 11, 15, 0))

            expected_response = {'status': 'ok'}
            link_api_url = '%s%s' % (
                self.live_server_url,
                reverse('api-link-usage', kwargs={'pk': self.link.pk}),
            )

            response = requests.post(
                link_api_url, data={'user': self.user.slug})
            self.assertEqual(response.status_code, 201)
            self.assertEquals(self.link.usage_total(), 2)
            self.assertEquals(response.json(), expected_response)

    # TODO - fix in later v of django
    # this test is commented out because of a bug in django
    # https://code.djangoproject.com/ticket/25251
    # which means tests will fail because the Link object doesn't exist
    # after the first TransactionTestCase has happened
    @skipIf(
        getenv('TEST_API_USAGE', None) is None,
        'Skipping tests that has to be run in isolation because of django bug'
    )
    def test_update_usage_creates_api_usage(self):
        api = Link.objects.get(pk=2)
        self.assertEquals(self.link.usage_total(), 0)
        self.assertEquals(api.usage_total(), 0)

        link_api_url = '%s%s' % (
            self.live_server_url,
            reverse('api-link-usage', kwargs={'pk': self.link.pk}),
        )

        expected_response = {'status': 'ok'}
        response = requests.post(
            link_api_url, data={'user': self.user.slug})

        self.assertEqual(response.status_code, 201)
        self.assertEquals(self.link.usage_total(), 1)
        self.assertEquals(response.json(), expected_response)

        self.assertEquals(api.usage_total(), 1)

    def test_cannot_update_usage_on_nonexistent_link(self):
        link_api_url = '%s%s' % (
            self.live_server_url,
            reverse('api-link-usage', kwargs={'pk': (self.link.pk + 1000)}),
        )

        response = requests.post(
            link_api_url, data={'user': self.user.userid})
        self.assertEqual(response.status_code, 404)
