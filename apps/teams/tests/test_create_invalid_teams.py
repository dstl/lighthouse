# (c) Crown Owned Copyright, 2016. Dstl.

from django.core.urlresolvers import reverse

from django_webtest import WebTest

from apps.organisations.models import Organisation
from apps.teams.models import Team
from testing.common import make_user, login_user


class TeamInvalidWebTest(WebTest):
    def setUp(self):
        self.logged_in_user = make_user()
        self.assertTrue(login_user(self, self.logged_in_user))

        self.org = Organisation.objects.create(
            name='First Organisation')
        self.existing_team = Team.objects.create(
            name='First Team',
            organisation=self.org)

        self.logged_in_user.teams.add(self.existing_team)

    def test_cannot_create_team_with_existing_name_when_managing_teams(self):
        update_teams_url = reverse(
            'user-update-teams',
            kwargs={'slug': self.logged_in_user.slug}
            )
        form = self.app.get(update_teams_url).form
        form['teamname'] = self.existing_team.name
        form['organisation'] = str(self.org.pk)

        response = form.submit()

        form = response.context['form']

        self.assertIn(
            'Team with this Name already exists.',
            form['name'].errors
        )
