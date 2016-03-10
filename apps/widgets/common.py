# (c) Crown Owned Copyright, 2016. Dstl.
# apps/widgets/common.py
from django.db import models

from apps.teams.models import Team
from apps.organisations.models import Organisation


#   Passing context in by assignment
def TopOrganisations():

    #   Get the 'top' 20 organisations ranked by number of teams
    organisations = Organisation.objects.all().annotate(
        count=models.Count('team')
    )
    show_more_organisations_link = len(organisations) > 20
    top_organisations = organisations.order_by('-count', 'name')[:20]
    return show_more_organisations_link, top_organisations


def TopTeams():
    #   Get the 'top' 20 teams ranked by number of members
    teams = Team.objects.all().annotate(count=models.Count('user'))
    show_more_teams_link = len(teams) > 20
    top_teams = teams.order_by('-count', 'name')[:20]
    return show_more_teams_link, top_teams
