# (c) Crown Owned Copyright, 2016. Dstl.

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta, SU
from unittest import mock

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils.timezone import now, make_aware

from django_webtest import WebTest

from ..models import Link
from .common import make_user, check_user


class LinkUsageModelTest(TestCase):
    def setUp(self):
        self.user = make_user()
        self.link = Link.objects.create(
            name='Link Linkerly',
            destination='link.com',
            owner=self.user,
            is_external=False,
        )
        self.other_link = Link.objects.create(
            name='Other Link',
            destination='otherlink.com',
            owner=self.user,
            is_external=True,
        )
        self.now = now()

    def test_usage(self):
        self.assertEquals(self.link.usage_total(), 0)
        self.assertEquals(self.other_link.usage_total(), 0)

        # register usage
        self.link.register_usage(self.user)

        self.assertEquals(self.link.usage_today(), 1)
        self.assertEquals(self.link.usage_total(), 1)
        self.assertEquals(self.other_link.usage_total(), 0)

    def test_usage_only_yesterday(self):
        self.assertEquals(self.link.usage_total(), 0)
        self.assertEquals(self.other_link.usage_total(), 0)

        with mock.patch('django.utils.timezone.now') as mock_now:
            # register usage yesterday
            mock_now.return_value = self.now - timedelta(days=1)
            self.link.register_usage(self.user)

        self.assertEquals(self.link.usage_today(), 0)
        self.assertEquals(self.link.usage_past_seven_days(), 1)
        self.assertEquals(self.link.usage_past_thirty_days(), 1)
        self.assertEquals(self.link.usage_total(), 1)
        self.assertEquals(self.other_link.usage_total(), 0)

    def test_usage_six_days_ago(self):
        self.assertEquals(self.link.usage_total(), 0)
        self.assertEquals(self.other_link.usage_total(), 0)

        with mock.patch('django.utils.timezone.now') as mock_now:
            # register usage six days ago
            mock_now.return_value = self.now - timedelta(days=6)
            self.link.register_usage(self.user)

        self.assertEquals(self.link.usage_today(), 0)
        self.assertEquals(self.link.usage_past_seven_days(), 1)
        self.assertEquals(self.link.usage_past_thirty_days(), 1)
        self.assertEquals(self.link.usage_total(), 1)
        self.assertEquals(self.other_link.usage_total(), 0)

    def test_usage_from_last_week(self):
        self.assertEquals(self.link.usage_total(), 0)
        self.assertEquals(self.other_link.usage_total(), 0)

        with mock.patch('django.utils.timezone.now') as mock_now:
            # register usage on last Sunday (doesn't count as "this week")
            mock_now.return_value = self.now + relativedelta(weekday=SU(-1))
            self.link.register_usage(self.user)

        self.assertEquals(self.link.usage_today(), 0)
        self.assertEquals(self.link.usage_this_week(), 0)
        self.assertEquals(self.link.usage_past_seven_days(), 1)
        self.assertEquals(self.link.usage_past_thirty_days(), 1)
        self.assertEquals(self.link.usage_total(), 1)
        self.assertEquals(self.other_link.usage_total(), 0)

    def test_usage_this_week(self):
        self.assertEquals(self.link.usage_total(), 0)
        self.assertEquals(self.other_link.usage_total(), 0)

        with mock.patch('django.utils.timezone.now') as mock_now:
            # register usage on a specific Tuesday
            mock_now.return_value = make_aware(datetime(2016, 3, 1, 10, 0, 0))
            self.link.register_usage(self.user)

            # test this counts as "this week" on the following Thursday
            mock_now.return_value = make_aware(datetime(2016, 3, 3, 12, 0, 0))

            self.assertEquals(self.link.usage_today(), 0)
            self.assertEquals(self.link.usage_this_week(), 1)
            self.assertEquals(self.link.usage_past_seven_days(), 1)
            self.assertEquals(self.link.usage_past_thirty_days(), 1)
            self.assertEquals(self.link.usage_total(), 1)
            self.assertEquals(self.other_link.usage_total(), 0)

    def test_usage_this_month(self):
        self.assertEquals(self.link.usage_total(), 0)
        self.assertEquals(self.other_link.usage_total(), 0)

        with mock.patch('django.utils.timezone.now') as mock_now:
            # register usage in a specific month
            mock_now.return_value = make_aware(datetime(2016, 3, 1, 10, 0, 0))
            self.link.register_usage(self.user)

            # register usage in the previous month
            mock_now.return_value = make_aware(datetime(2016, 2, 29, 10, 0, 0))
            self.link.register_usage(self.user)

            # test it from the point of view of the specific month
            mock_now.return_value = make_aware(datetime(2016, 3, 3, 12, 0, 0))

            self.assertEquals(self.link.usage_today(), 0)
            self.assertEquals(self.link.usage_this_week(), 2)
            self.assertEquals(self.link.usage_past_seven_days(), 2)
            self.assertEquals(self.link.usage_past_thirty_days(), 2)
            self.assertEquals(self.link.usage_this_month(), 1)
            self.assertEquals(self.link.usage_total(), 2)
            self.assertEquals(self.other_link.usage_total(), 0)


class LinkUsageWebTest(WebTest):
    def setUp(self):
        self.user = make_user()
        self.assertTrue(check_user(self, self.user))

        self.link = Link.objects.create(
            name='Link Linkerly',
            destination='/',
            owner=self.user,
            is_external=False,
        )
        self.other_link = Link.objects.create(
            name='Other Link',
            destination='/links',
            owner=self.user,
            is_external=True,
        )

    def test_internal_link_usage(self):
        detail_url = reverse('link-detail', kwargs={'pk': self.link.pk})

        response = self.app.get(detail_url)
        usage_today = response.html.find(id='usage-today').find('em').text
        self.assertEquals(response.html.h1.text, 'Link Linkerly')
        self.assertEquals(usage_today, '0')

        # going to the tool registers usage
        response.click(linkid='link_follow_button').follow()

        response = self.app.get(detail_url)
        usage_today = response.html.find(id='usage-today').find('em').text
        self.assertEquals(response.html.h1.text, 'Link Linkerly')
        self.assertEquals(usage_today, '1')

    def test_external_link_usage(self):
        detail_url = reverse('link-detail', kwargs={'pk': self.other_link.pk})

        response = self.app.get(detail_url)
        usage_today = response.html.find(id='usage-today').find('em').text
        self.assertEquals(response.html.h1.text, 'Other Link')
        self.assertEquals(usage_today, '0')

        # going to the interstitial page does not register usage
        response.click(linkid='link_follow_button').follow()

        response = self.app.get(detail_url)
        usage_today = response.html.find(id='usage-today').find('em').text
        self.assertEquals(response.html.h1.text, 'Other Link')
        self.assertEquals(usage_today, '0')

        # clicking 'yes' on interstitial does register usage
        interstitial = response.click(linkid='link_follow_button').follow()
        interstitial.form.submit()

        response = self.app.get(detail_url)
        usage_today = response.html.find(id='usage-today').find('em').text
        self.assertEquals(response.html.h1.text, 'Other Link')
        self.assertEquals(usage_today, '1')
