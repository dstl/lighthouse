# (c) Crown Owned Copyright, 2016. Dstl.

from django.core.urlresolvers import reverse

from django_webtest import WebTest

from .common import create_organisation
from apps.links.tests.common import generate_fake_links
from apps.users.models import User


class OrganisationDetailWebTest(WebTest):
    def test_new_team_input_visible(self):
        #   Create and log in a user
        User(slug='user0001com', original_slug='user@0001.com').save()
        form = self.app.get(reverse('login-view')).form
        form['slug'] = 'user0001com'
        form.submit().follow()

        o = create_organisation(name='two teams', num_teams=2)
        response = self.app.get(
            reverse(
                'organisation-detail',
                kwargs={'pk': o.pk}
            )
        )

        new_team_input = response.html.find('input', {"id": "id_new_team"})
        team_list = response.html.find("ul", {"class": "team-list"})

        self.assertEqual(len(team_list.findChildren(
            "a",
            {"class": "main-list-item"}
        )), 2)
        self.assertIsNotNone(new_team_input)

        return response, o

    def test_can_add_new_team(self):
        response, o = self.test_new_team_input_visible()

        form = response.form
        form['name'] = 'The Newest Team'

        response = form.submit().follow()
        new_team_input = response.html.find('input', {"id": "id_new_team"})
        team_list = response.html.find("ul", {"class": "team-list"})
        team_list_items = team_list.findChildren(
            "a",
            {"class": "main-list-item"}
        )

        self.assertEqual(len(team_list_items), 3)
        self.assertIn('The Newest Team', team_list_items[2].text)
        self.assertIsNotNone(new_team_input)

        return response, o

    def test_cannot_add_duplicate_new_team(self):
        response, o = self.test_can_add_new_team()

        form = response.form
        form['name'] = 'The Newest Team'
        response = form.submit()
        form = response.form

        self.assertIn(o.name, response.html.find('h1').text)
        self.assertNotIn("Team", response.html.find('h1').text)

        error_list = response.html.find(id="id_name_error_list")
        org_label = response.html.find(id="organisation_label")
        error_list_items = error_list.findChildren("li")

        self.assertIn(o.name, org_label.text)
        self.assertIsNotNone(error_list)
        self.assertEqual(len(error_list_items), 1)
        self.assertEqual(
            int(form['organisation'].value), o.id,
            "The organisation from the previous page should be selected"
        )
        self.assertEqual(form['name'].value, 'The Newest Team')

        return response, o

    # This came about when I noticed that re-submitting the form causes the
    # UI to show all orgs. It should do exactly what it does the first time.
    def test_cannot_add_duplicate_new_team_second_attempt(self):
        response, o = self.test_cannot_add_duplicate_new_team()

        form = response.form
        response = form.submit()
        form = response.form

        self.assertIn(o.name, response.html.find('h1').text)
        self.assertNotIn("Team", response.html.find('h1').text)

        error_list = response.html.find(id="id_name_error_list")
        org_label = response.html.find(id="organisation_label")
        error_list_items = error_list.findChildren("li")

        self.assertIn(o.name, org_label.text)
        self.assertIsNotNone(error_list)
        self.assertEqual(len(error_list_items), 1)
        self.assertEqual(
            int(form['organisation'].value), o.id,
            "The organisation from the previous page should be selected"
        )
        self.assertEqual(form['name'].value, 'The Newest Team')

        return response, o

    def test_can_rename_team_duplicate_new_team(self):
        response, o = self.test_cannot_add_duplicate_new_team()

        form = response.form
        form['name'] = 'The Newest Team 2'
        response = form.submit().follow()
        form = response.form

        team_list = response.html.find("ul", {"class": "team-list"})
        team_list_items = team_list.findChildren(
            "a",
            {"class": "main-list-item"}
        )

        self.assertEqual(len(team_list_items), 4)
        self.assertIn('The Newest Team 2', team_list_items[3].text)

    def test_list_top_tools_ordered(self):
        #   Create and log in a user
        User(slug='user0001com', original_slug='user@0001.com').save()
        form = self.app.get(reverse('login-view')).form
        form['slug'] = 'user0001com'
        form.submit().follow()

        # Create an organistion with two teams and two members in each team.
        o = create_organisation(
            name='Two members two teams top orgs', num_teams=2, num_members=2
        )

        t1 = o.team_set.all()[0]
        t2 = o.team_set.all()[1]

        user1 = t1.user_set.all()[0]
        user2 = t2.user_set.all()[0]

        (self.el1, self.el2,
         self.el3, self.el4,
         self.el5, self.el6,
         self.el7, self.el8,
         self.el9, self.el10) = generate_fake_links(
            user1,
            count=10,
            is_external=True
        )

        # Register a user from each team as having used various tools to
        # increase the aggregate from values across teams.
        # 16 times for existing link 8
        for i in range(0, 6):
            self.el8.register_usage(user1)
        for i in range(0, 10):
            self.el8.register_usage(user2)

        # 13 times for existing link 4
        for i in range(0, 8):
            self.el4.register_usage(user1)
        for i in range(0, 5):
            self.el4.register_usage(user2)

        # 9 times for existing link 1
        for i in range(0, 4):
            self.el1.register_usage(user1)
        for i in range(0, 5):
            self.el1.register_usage(user2)

        # 8 times for existing link 3
        for i in range(0, 5):
            self.el3.register_usage(user1)
        for i in range(0, 3):
            self.el3.register_usage(user2)

        # 4 times for existing link 9
        for i in range(0, 3):
            self.el9.register_usage(user1)
        for i in range(0, 1):
            self.el9.register_usage(user2)

        # 3 times for existing link 10
        for i in range(0, 2):
            self.el10.register_usage(user1)
        for i in range(0, 1):
            self.el10.register_usage(user2)

        response = self.app.get(reverse(
            'organisation-detail',
            kwargs={"pk": o.pk}
        ))

        tools_list = response.html.find(id="top_links_list")
        tools_list_items = tools_list.findChildren('a')

        self.assertEqual(
            len(tools_list_items),
            5
        )
        self.assertIn(
            self.el8.name,
            tools_list_items[0].text
        )
        self.assertIn(
            self.el4.name,
            tools_list_items[1].text
        )
        self.assertIn(
            self.el1.name,
            tools_list_items[2].text
        )
        self.assertIn(
            self.el3.name,
            tools_list_items[3].text
        )
        self.assertIn(
            self.el9.name,
            tools_list_items[4].text
        )
        self.assertNotIn(
            self.el10.name,
            tools_list.text
        )
        self.assertNotIn(
            self.el2.name,
            tools_list.text
        )
        self.assertNotIn(
            self.el5.name,
            tools_list.text
        )
        self.assertNotIn(
            self.el6.name,
            tools_list.text
        )
        self.assertNotIn(
            self.el7.name,
            tools_list.text
        )
