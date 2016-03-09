# (c) Crown Owned Copyright, 2016. Dstl.
from django.core.urlresolvers import reverse
from django_webtest import WebTest

from .common import create_organisation


class OrganisationDetailWebTest(WebTest):
    def test_new_team_input_visible(self):
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

        return response

    def test_can_add_new_team(self):
        response = self.test_new_team_input_visible()

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
