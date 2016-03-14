# (c) Crown Owned Copyright, 2016. Dstl.
# apps/teams/tests.py
from django.core.urlresolvers import reverse
from django_webtest import WebTest
import re
from apps.teams.models import Team
from apps.organisations.models import Organisation
from .common import create_team


class TeamWebTest(WebTest):
    def test_can_click_through_existing_team_link(self):
        o = Organisation(name='New Org')
        o.save()
        team_name = 'New Team skippity bippity bop'
        t = Team(name=team_name, organisation=o)
        t.save()
        response = self.app.get(reverse('team-list'))
        response = self.app.get(response.html.find(
                'a',
                text=re.compile(team_name + r'')
            ).attrs['href']
        )
        org_name = response.html.find(
            'h1',
            attrs={'class': 'heading-xlarge'}
        ).text
        self.assertEquals(org_name, 'Team: ' + team_name)

    def test_show_number_of_members_two(self):
        t = create_team(name='two members', num_members=2)
        response = self.app.get(reverse('team-list'))

        self.assertIn(
            t.name,
            response.html.find('a', {"class": "main-list-item"}).text
        )
        self.assertIn(
            'Total members: 2',
            response.html.find('ul', {"class": "team-info"}).text
        )

    def test_show_number_of_members_none(self):
        t = create_team(name='no members', num_members=0)
        response = self.app.get(reverse('team-list'))

        self.assertIn(
            t.name,
            response.html.find('a', {"class": "main-list-item"}).text
        )
        self.assertIn(
            'This team has no members',
            response.html.find('ul', {"class": "team-info"}).text
        )

    def test_list_members(self):
        t = create_team(name='two members', num_members=2)
        response = self.app.get(reverse('team-detail', kwargs={"pk": t.pk}))

        user_items = response.html.find(
            'ul',
            {"class": "member-list"}
        ).findChildren('li')

        self.assertEqual(
            len(user_items),
            2
        )

        self.assertIn(
            'Team Member 1',
            user_items[0].text
        )

        self.assertIn(
            'Team Member 2',
            user_items[1].text
        )

    def test_list_members_no_username(self):
        t = create_team(
            name='two members', num_members=2,
            usernames={0: None, 1: 'steve'}
        )
        response = self.app.get(reverse('team-detail', kwargs={"pk": t.pk}))

        user_items = response.html.find(
            'ul',
            {"class": "member-list"}
        ).findChildren('li')

        self.assertEqual(
            len(user_items),
            2
        )

        self.assertIn(
            'teammember1',
            user_items[0].text
        )

        self.assertIn(
            'steve',
            user_items[1].text
        )

    def test_list_members_names_link(self):
        t = create_team(
            name='two members', num_members=1
        )
        response = self.app.get(reverse('team-detail', kwargs={"pk": t.pk}))

        user_links = response.html.find(
            'ul',
            {"class": "member-list"}
        ).findChildren('a')

        self.assertEqual(
            len(user_links),
            1
        )

        response = response.click(user_links[0].text)

        self.assertIn(
            'Team Member 1',
            response.html.find(
                'h1', {"class": "form-title"}
            ).text
        )
