# (c) Crown Owned Copyright, 2016. Dstl.
# apps/teams/tests.py
from django.core.urlresolvers import reverse
from django_webtest import WebTest
from django.test import TestCase
from django.db.utils import IntegrityError

from .models import Team
from apps.organisations.models import Organisation
from apps.users.models import User


def create_team(name, num_members=0, usernames={}):
    o = Organisation(name="Organisation for %s" % name)
    o.save()
    t = Team(name=name, organisation=o)
    t.save()
    # pdb.set_trace()
    for x in range(0, num_members):
        if x in usernames.keys():
            username = usernames[x]
        else:
            username = 'Team Member %d' % (x + 1)

        u = User(
            slug='teammember%d' % (x + 1)
        )

        if username is not None:
            u.username = username

        u.save()
        u.teams.add(t)
        u.save()
        t.save()
    return t


class TeamTest(TestCase):
    def setUp(self):
        o = Organisation(name='Existing Org')
        o.save()
        t = Team(name='Existing Team', organisation=o)
        t.save()

    def test_cannot_add_team_without_organisation(self):
        t = Team(name='New Team')
        self.assertIsNone(t.pk)

    #   Wut???? TODO: De-Wutify this...
    #   How do we test for ValueError?
    """
    def test_cannot_add_team_with_not_organisation(self):
        o = Organisation(name='New Org')
        o.save()
        t1 = Team(name='New Team 1', organisation=o)
        t1.save()
        t2 = Team(name='New Team 2', organisation=t1)
        self.assertRaises(ValueError, t2.save())
    """

    def test_cannot_create_duplicate_team(self):
        t = Team(name='Existing Team')
        with self.assertRaises(IntegrityError):
            t.save()

    def test_can_create_team(self):
        o = Organisation(name='New Org')
        o.save()
        self.assertTrue(o.pk)
        t = Team(name='New Team', organisation=o)
        t.save()
        self.assertTrue(t.pk)


class TeamWebTest(WebTest):
    def test_cannot_create_nameless_team(self):
        form = self.app.get(reverse('team-create')).form
        response = form.submit()
        form = response.context['form']
        self.assertIn(
            'This field is required.',
            form['name'].errors
        )

    def test_cannot_create_organisationless_team(self):
        form = self.app.get(reverse('team-create')).form
        form['name'] = 'New Team'
        response = form.submit()
        html = response.html
        errors = html.find(
            "ul",
            {"class": "form-error-list"}
        ).find("li").contents

        self.assertEqual(len(errors), 1)

        self.assertIn(
            'You must select an existing organisation or create a new one.',
            errors[0].text
        )

    def test_cannot_create_org_and_new_org_team(self):
        o = Organisation(name='New Org')
        o.save()
        form = self.app.get(reverse('team-create')).form
        form['name'] = 'New Team'
        form['organisation'] = str(o.pk)
        form['new_organisation'] = 'New Org'
        response = form.submit()
        html = response.html
        errors = html.find(
            "ul",
            {"class": "form-error-list"}
        ).find("li").contents

        self.assertEqual(len(errors), 1)

        failMessage = "You can't select an existing organisation and "
        failMessage += "create a new one at the same time."
        self.assertIn(failMessage, errors[0].text)

    def test_can_create_team_with_existsing_org(self):
        o = Organisation(name='New Org')
        o.save()
        team_name = 'New Team skippity bippity bop'
        form = self.app.get(reverse('team-create')).form
        form['name'] = team_name
        form['organisation'] = str(o.pk)
        response = form.submit().follow()
        self.assertEquals(response.status_int, 200)
        html = response.html
        links = html.findAll("a", text=team_name)[0].contents
        self.assertIn(team_name, links)

    def test_can_create_team_with_new_org(self):
        org_name = 'New Org'
        team_name = 'New Team skippity bippity bop'
        form = self.app.get(reverse('team-create')).form
        form['name'] = team_name
        form['new_organisation'] = org_name
        response = form.submit().follow()
        self.assertEquals(response.status_int, 200)
        html = response.html
        links = html.findAll("a", text=team_name)[0].contents
        self.assertIn(team_name, links)
        #   But we also need to test that the organisation now exists in
        #   the db.
        check_org = Organisation.objects.filter(name=org_name).exists()
        self.assertTrue(check_org)

    def test_can_create_team_from_list_view(self):
        org_name = 'New Org'
        team_name = 'New Team skippity bippity bop'
        form = self.app.get(reverse('team-list')).form
        form['name'] = team_name
        form['new_organisation'] = org_name
        response = form.submit()
        self.assertEquals(response.status_int, 302)

        response = self.app.get(reverse('team-list'))
        response = response.click(team_name)
        org_name = response.html.find(
            'h1',
            attrs={'class': 'heading-xlarge'}
        ).text
        self.assertEquals(org_name, 'Team: ' + team_name)

    def test_can_click_through_existing_team_link(self):
        o = Organisation(name='New Org')
        o.save()
        team_name = 'New Team skippity bippity bop'
        t = Team(name=team_name, organisation=o)
        t.save()
        response = self.app.get(reverse('team-list'))
        response = response.click(team_name)
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
        # pdb.set_trace()
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
