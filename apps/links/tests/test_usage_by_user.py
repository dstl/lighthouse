# (c) Crown Owned Copyright, 2016. Dstl.
from dateutil.relativedelta import relativedelta
from unittest import mock

from django.core.urlresolvers import reverse
# from django.test import TestCase
from django.utils.timezone import now

from django_webtest import WebTest

# from ..models import Link
# from .common import make_user, login_user
from apps.organisations.tests.common import create_organisation
from apps.links.tests.common import generate_fake_links


def register_link_usage_for_user(link, user, num_usage):
    for u in range(0, num_usage):
        link.register_usage(user)


class LinkUsageByUserTest(WebTest):
    def setUp(self):
        org = create_organisation(
            'Heavy Users',
            num_teams=1,
            num_members=8,
        )
        # user variable names here are ordered by usage
        self.top_user_1 = org.team_set.all()[0].user_set.all()[4]
        self.top_user_2 = org.team_set.all()[0].user_set.all()[2]
        self.top_user_3 = org.team_set.all()[0].user_set.all()[3]
        self.top_user_4 = org.team_set.all()[0].user_set.all()[1]
        self.top_user_5 = org.team_set.all()[0].user_set.all()[0]
        self.top_user_6 = org.team_set.all()[0].user_set.all()[6]

        self.owner_user = org.team_set.all()[0].user_set.all()[5]

        self.used_link, = generate_fake_links(self.owner_user, 2)

        register_link_usage_for_user(self.used_link, self.top_user_1, 13)
        register_link_usage_for_user(self.used_link, self.top_user_2, 12)
        register_link_usage_for_user(self.used_link, self.top_user_3, 10)
        register_link_usage_for_user(self.used_link, self.top_user_4, 9)
        register_link_usage_for_user(self.used_link, self.top_user_5, 7)
        register_link_usage_for_user(self.used_link, self.top_user_6, 5)
        register_link_usage_for_user(self.used_link, self.owner_user, 4)

        # We need this for time mocking.
        self.now = now()

    def test_top_users(self):
        users = self.used_link.top_users_thirty_days()

        first_user = users[0]

        self.assertEqual(first_user, self.top_user_1)
        self.assertEqual(first_user.link_usage_count, 13)

        self.assertEqual(len(users), 7)

    def test_five_users_of_tool_listed_in_usage_order(self):
        response = self.app.get(
            reverse('link-detail', kwargs={'pk': self.used_link.pk})
        )

        user_usage = response.html.find("ul", {"id": "usage-by-users"})
        self.assertIsNotNone(user_usage)

        user_usage_items = user_usage.findChildren("li")

        self.assertEqual(5, len(user_usage_items))

        self.assertIn(self.top_user_1.username, user_usage_items[0].text)
        self.assertIn('13', user_usage_items[0].text)
        self.assertIn(self.top_user_2.username, user_usage_items[1].text)
        self.assertIn('12', user_usage_items[1].text)
        self.assertIn(self.top_user_3.username, user_usage_items[2].text)
        self.assertIn('10', user_usage_items[2].text)
        self.assertIn(self.top_user_4.username, user_usage_items[3].text)
        self.assertIn('9', user_usage_items[3].text)
        self.assertIn(self.top_user_5.username, user_usage_items[4].text)
        self.assertIn('7', user_usage_items[4].text)

    def test_five_users_of_tool_listed_in_usage_order_excluding_old(self):
        with mock.patch('django.utils.timezone.now') as mock_now:
            # Register additional usage, just within the window
            mock_now.return_value = self.now - relativedelta(days=29)
            self.used_link.register_usage(self.top_user_1)

            # Register additional usage, AGES ago (just outside window)
            mock_now.return_value = self.now - relativedelta(days=31)
            self.used_link.register_usage(self.top_user_1)

        response = self.app.get(
            reverse('link-detail', kwargs={'pk': self.used_link.pk})
        )

        user_usage = response.html.find("ul", {"id": "usage-by-users"})
        self.assertIsNotNone(user_usage)

        user_usage_items = user_usage.findChildren("li")

        self.assertEqual(5, len(user_usage_items))

        self.assertIn(self.top_user_1.username, user_usage_items[0].text)
        self.assertIn('14', user_usage_items[0].text)
        self.assertIn(self.top_user_2.username, user_usage_items[1].text)
        self.assertIn('12', user_usage_items[1].text)
        self.assertIn(self.top_user_3.username, user_usage_items[2].text)
        self.assertIn('10', user_usage_items[2].text)
        self.assertIn(self.top_user_4.username, user_usage_items[3].text)
        self.assertIn('9', user_usage_items[3].text)
        self.assertIn(self.top_user_5.username, user_usage_items[4].text)
        self.assertIn('7', user_usage_items[4].text)
