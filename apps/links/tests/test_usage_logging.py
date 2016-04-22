# (c) Crown Owned Copyright, 2016. Dstl.

import csv
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta, SU
from unittest import mock

from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils.timezone import now, make_aware

from django_webtest import WebTest

from ..models import Link
from testing.common import make_user, login_user


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

        usage = self.link.usage.all()[0]
        self.assertEquals(usage.duration, 0)

    def test_update_usage_within_one_hour(self):
        self.assertEquals(self.link.usage_total(), 0)
        self.assertEquals(self.other_link.usage_total(), 0)

        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = make_aware(datetime(2016, 3, 1, 10, 0, 0))
            self.link.register_usage(self.user)

            mock_now.return_value = make_aware(datetime(2016, 3, 1, 10, 59, 0))
            self.link.register_usage(self.user)

            self.assertEquals(self.link.usage_today(), 1)
            self.assertEquals(self.link.usage_total(), 1)
            self.assertEquals(self.other_link.usage_total(), 0)

        usage = self.link.usage.all()[0]
        self.assertEquals(usage.duration, 3540)

    def test_update_different_user_doesnt_cause_duration(self):
        self.assertEquals(self.link.usage_total(), 0)
        self.assertEquals(self.other_link.usage_total(), 0)

        new_user = make_user(userid='user@example.com')
        self.link.register_usage(self.user)
        self.link.register_usage(new_user)

        self.assertEquals(self.link.usage_today(), 2)
        self.assertEquals(self.link.usage_total(), 2)
        self.assertEquals(self.other_link.usage_total(), 0)

    def test_update_different_link_doesnt_cause_duration(self):
        self.assertEquals(self.link.usage_total(), 0)
        self.assertEquals(self.other_link.usage_total(), 0)

        self.link.register_usage(self.user)
        self.other_link.register_usage(self.user)

        self.assertEquals(self.link.usage_today(), 1)
        self.assertEquals(self.link.usage_total(), 1)
        self.assertEquals(self.other_link.usage_today(), 1)
        self.assertEquals(self.other_link.usage_total(), 1)

    def test_create_new_usage_after_one_hour(self):
        self.assertEquals(self.link.usage_total(), 0)
        self.assertEquals(self.other_link.usage_total(), 0)

        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = make_aware(datetime(2016, 3, 1, 10, 0, 0))
            self.link.register_usage(self.user)

            mock_now.return_value = make_aware(datetime(2016, 3, 1, 11, 0, 0))
            self.link.register_usage(self.user)

            self.assertEquals(self.link.usage_today(), 2)
            self.assertEquals(self.link.usage_total(), 2)
            self.assertEquals(self.other_link.usage_total(), 0)

        usage = self.link.usage.all()
        self.assertEquals(usage[0].duration, 0)
        self.assertEquals(usage[1].duration, 0)

    def test_force_new_usage(self):
        self.assertEquals(self.link.usage_total(), 0)
        self.assertEquals(self.other_link.usage_total(), 0)

        with mock.patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = make_aware(datetime(2016, 3, 1, 10, 0, 0))
            self.link.register_usage(self.user)

            mock_now.return_value = make_aware(datetime(2016, 3, 1, 10, 15, 0))
            self.link.register_usage(self.user, force_new=True)

            self.assertEquals(self.link.usage_today(), 2)
            self.assertEquals(self.link.usage_total(), 2)
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
            mock_now.return_value = make_aware(datetime(2016, 2, 29, 10, 0, 0))
            self.link.register_usage(self.user)

            # register usage in the next month
            mock_now.return_value = make_aware(datetime(2016, 3, 1, 10, 0, 0))
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
        self.assertTrue(login_user(self, self.user))

        self.link = Link.objects.create(
            name='Link Linkerly',
            destination='https://here/',
            owner=self.user,
            is_external=False,
        )
        self.other_link = Link.objects.create(
            name='Other Link',
            destination='https://here/links',
            owner=self.user,
            is_external=True,
        )
        self.now = now()

    def test_overall_stats_page(self):
        with mock.patch('django.utils.timezone.now') as mock_now:
            # register usage eight days ago
            mock_now.return_value = self.now - relativedelta(days=8)
            self.link.register_usage(self.user)

            # register usage thirty-eight days ago
            mock_now.return_value = self.now - relativedelta(days=38)
            self.link.register_usage(self.user)

        self.link.register_usage(self.user)
        self.other_link.register_usage(self.user)

        stats_url = reverse('link-overall-stats')
        response = self.app.get(stats_url)

        link_stats = response.html.find('tr', id='stats-for-%d' % self.link.pk)
        other_link_stats = response.html.find('tr', id='stats-for-%d' %
                                              self.other_link.pk)

        link_stats_cells = link_stats.findChildren('td')
        other_link_stats_cells = other_link_stats.findChildren('td')

        # Name
        self.assertIn(
            self.link.name,
            link_stats_cells[0].get_text(strip=True)
        )
        self.assertEquals(
            other_link_stats_cells[0].get_text(strip=True),
            '%sExternal' % self.other_link.name,
        )

        # Thirty
        self.assertEquals(link_stats_cells[1].text, '2')
        self.assertEquals(other_link_stats_cells[1].text, '1')

        # Seven Days
        self.assertEquals(link_stats_cells[2].text, '1')
        self.assertEquals(other_link_stats_cells[2].text, '1')

        # Total
        self.assertEquals(link_stats_cells[3].text, '2')
        self.assertEquals(other_link_stats_cells[3].text, '1')

    def test_link_stats_page_excludes_api(self):
        lighthouse_api_link = Link.objects.get(id=2)
        lighthouse_api_link.register_usage(self.user)

        stats_url = reverse('link-overall-stats')
        response = self.app.get(stats_url)

        api_stats = response.html.find('tr', id='stats-for-2')

        self.assertIsNone(api_stats)

    def test_internal_link_usage(self):
        detail_url = reverse('link-detail', kwargs={'pk': self.link.pk})

        response = self.app.get(detail_url)
        usage_today = response.html.find(id='usage-today').find(
            'span',
            {"class": "stat-inline"}
        ).get_text(strip=True)
        self.assertEquals(
            response.html.h1.get_text(strip=True),
            'ToolLink Linkerly'
        )
        self.assertEquals(usage_today, '0')

        #   Check that this link *doesn't* appear in the 'top tools' widget
        user_response = self.app.get(
            reverse('user-detail', kwargs={'slug': self.user.slug})
        )
        self.assertIsNone(
            user_response.html.find(
                id='top_links_for_user'
            ).find('a', text='Link Linkerly')
        )

        # going to the tool registers usage
        response.click(linkid='link_follow_button').follow()

        response = self.app.get(detail_url)
        usage_today = response.html.find(id='usage-today').find(
            'span',
            {"class": "stat-inline"}
        ).get_text(strip=True)
        self.assertEquals(
            response.html.h1.get_text(strip=True),
            'ToolLink Linkerly'
        )
        self.assertEquals(usage_today, '1')

        #   Check that this link does appear in the 'top tools' widget
        user_response = self.app.get(
            reverse('user-detail', kwargs={'slug': self.user.slug})
        )
        self.assertTrue(
            user_response.html.find(
                id='top_links_for_user'
            ).find('a', text='Link Linkerly')
        )

    def test_external_link_usage(self):
        detail_url = reverse('link-detail', kwargs={'pk': self.other_link.pk})

        response = self.app.get(detail_url)
        usage_today = response.html.find(id='usage-today').find(
            'span',
            {"class": "stat-inline"}
        ).get_text(strip=True)
        self.assertEquals(
            response.html.h1.get_text(strip=True),
            'ToolOther Link'
        )
        self.assertEquals(usage_today, '0')

        #   Check that this link *doesn't* appear in the 'top tools' widget
        user_response = self.app.get(
            reverse('user-detail', kwargs={'slug': self.user.slug})
        )
        self.assertIsNone(
            user_response.html.find(
                id='top_links_for_user'
            ).find('a', text='Other Link')
        )

        # going to the interstitial page does not register usage
        response.click(linkid='link_follow_button').follow()

        response = self.app.get(detail_url)
        usage_today = response.html.find(id='usage-today').find(
            'span',
            {"class": "stat-inline"}
        ).get_text(strip=True)
        self.assertEquals(
            response.html.h1.get_text(strip=True),
            'ToolOther Link'
        )
        self.assertEquals(usage_today, '0')

        # clicking 'yes' on interstitial does register usage
        interstitial = response.click(linkid='link_follow_button').follow()
        interstitial.form.submit()

        response = self.app.get(detail_url)
        usage_today = response.html.find(id='usage-today').find(
            'span',
            {"class": "stat-inline"}
        ).get_text(strip=True)
        self.assertEquals(
            response.html.h1.get_text(strip=True),
            'ToolOther Link'
        )
        self.assertEquals(usage_today, '1')

        #   Check that this link does appear in the 'top tools' widget
        user_response = self.app.get(
            reverse('user-detail', kwargs={'slug': self.user.slug})
        )
        self.assertTrue(
            user_response.html.find(
                id='top_links_for_user'
            ).find('a', text='Other Link')
        )

    def test_link_stats_page(self):
        with mock.patch('django.utils.timezone.now') as mock_now:
            # register usage thirty-eight days ago
            mock_now.return_value = self.now - relativedelta(days=38)
            self.link.register_usage(self.user)

            # register usage eight days ago
            mock_now.return_value = self.now - relativedelta(days=8)
            self.link.register_usage(self.user)

        # register usage now
        self.link.register_usage(self.user)

        stats_url = reverse('link-stats', kwargs={'pk': self.link.pk})
        response = self.app.get(stats_url)

        self.assertEquals(
            response.html.find(class_='usage-seven-days').text,
            '1'
        )
        self.assertEquals(
            response.html.find(class_='usage-thirty-days').text,
            '2'
        )
        self.assertEquals(
            response.html.find(class_='usage-total').text,
            '3'
        )

    def test_link_stats_csv(self):
        with mock.patch('django.utils.timezone.now') as mock_now:
            # register usage at a specific date
            mock_now.return_value = make_aware(datetime(2016, 3, 1, 10, 0, 0))
            self.link.register_usage(self.user)
            mock_now.return_value = make_aware(datetime(2016, 3, 1, 11, 15, 0))
            self.link.register_usage(self.user)

        stats_url = reverse('link-stats-csv', kwargs={'pk': self.link.pk})
        response = self.app.get(stats_url)
        lines = response.body.decode().split("\r\n")
        dialect = csv.Sniffer().sniff(response.body.decode())
        reader = csv.DictReader(lines, dialect=dialect)

        row = next(reader)
        self.assertEquals(row, {
            'User': 'user@0001.com',
            'Duration': '0',
            'Date': '2016-03-01 10:00:00',
            'Tool': 'Link Linkerly',
        })

        row = next(reader)
        self.assertEquals(row, {
            'User': 'user@0001.com',
            'Duration': '0',
            'Date': '2016-03-01 11:15:00',
            'Tool': 'Link Linkerly',
        })

    def test_overall_stats_csv(self):
        with mock.patch('django.utils.timezone.now') as mock_now:
            # register usage at specific times
            mock_now.return_value = make_aware(datetime(2016, 3, 1, 10, 0, 0))
            self.link.register_usage(self.user)

            # these two will be combined into usage with duration
            mock_now.return_value = make_aware(datetime(2016, 3, 1, 11, 15, 0))
            self.other_link.register_usage(self.user)
            mock_now.return_value = make_aware(datetime(2016, 3, 1, 11, 16, 0))
            self.other_link.register_usage(self.user)

            mock_now.return_value = make_aware(datetime(2016, 3, 1, 13, 0, 0))
            self.link.register_usage(self.user)

        stats_url = reverse('link-overall-stats-csv')
        response = self.app.get(stats_url)
        lines = response.body.decode().split("\r\n")
        dialect = csv.Sniffer().sniff(response.body.decode())
        reader = csv.DictReader(lines, dialect=dialect)

        row = next(reader)
        self.assertEquals(row, {
            'User': 'user@0001.com',
            'Duration': '0',
            'Date': '2016-03-01 10:00:00',
            'Tool': 'Link Linkerly',
            'External?': '',
        })

        row = next(reader)
        self.assertEquals(row, {
            'User': 'user@0001.com',
            'Duration': '60',
            'Date': '2016-03-01 11:15:00',
            'Tool': 'Other Link',
            'External?': 'External',
        })

        row = next(reader)
        self.assertEquals(row, {
            'User': 'user@0001.com',
            'Duration': '0',
            'Date': '2016-03-01 13:00:00',
            'Tool': 'Link Linkerly',
            'External?': '',
        })

    def test_usage_detail_page_three_periods(self):
        self.assertEquals(self.link.usage_total(), 0)
        self.assertEquals(self.other_link.usage_total(), 0)

        with mock.patch('django.utils.timezone.now') as mock_now:
            # register usage eight days ago (last 30 days)
            mock_now.return_value = self.now - timedelta(days=8)
            self.link.register_usage(self.user)

            # register usage one day ago (last 7 days)
            mock_now.return_value = self.now - timedelta(days=1)
            self.link.register_usage(self.user)

        # register usage today
        self.link.register_usage(self.user)

        detail_url = reverse('link-detail', kwargs={'pk': self.link.pk})
        response = self.app.get(detail_url)

        usage_today = response.html.find(id='usage-today').find(
            'span',
            {"class": "stat-inline"}
        ).text
        self.assertEquals(usage_today, '1')
        self.assertNotIn(
            '1 times',
            response.html.find(id='usage-today').text
        )

        usage_today = response.html.find(id='usage-seven-days').find(
            'span',
            {"class": "stat-inline"}
        ).text
        self.assertEquals(usage_today, '2')
        self.assertIn(
            '2 times',
            response.html.find(id='usage-seven-days').text
        )

        usage_today = response.html.find(id='usage-thirty-days').find(
            'span',
            {"class": "stat-inline"}
        ).text
        self.assertEquals(usage_today, '3')
        self.assertIn(
            '3 times',
            response.html.find(id='usage-thirty-days').text
        )

    def test_usage_detail_page_plurals(self):
        self.assertEquals(self.link.usage_total(), 0)
        self.assertEquals(self.other_link.usage_total(), 0)

        # register usage today
        self.link.register_usage(self.user)

        detail_url = reverse('link-detail', kwargs={'pk': self.link.pk})
        response = self.app.get(detail_url)

        self.assertNotIn(
            '1 times',
            response.html.find(id='usage-today').text
        )
        self.assertNotIn(
            '1 times',
            response.html.find(id='usage-seven-days').text
        )
        self.assertNotIn(
            '1 times',
            response.html.find(id='usage-thirty-days').text
        )
