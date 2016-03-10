# (c) Crown Owned Copyright, 2016. Dstl.
from apps.organisations.models import Organisation
from apps.teams.models import Team


def create_organisation(name, num_teams=0):
    o = Organisation(name=name)
    o.save()
    for x in range(0, num_teams):
        Team(name='New Team %d' % (x + 1), organisation=o).save()
    return o
