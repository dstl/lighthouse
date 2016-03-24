# (c) Crown Owned Copyright, 2016. Dstl.

from apps.organisations.models import Organisation
from apps.teams.models import Team
from apps.users.models import User


def create_organisation(name, num_teams=0, num_members=0, usernames={}):
    o = Organisation(name=name)
    o.save()
    user_global_id = 0
    for x in range(0, num_teams):
        t = Team(name='New Team %d' % (x + 1), organisation=o)
        t.save()
        for y in range(user_global_id, num_members + user_global_id):
            if y in usernames.keys():
                username = usernames[y]
            else:
                username = 'Team Member %d' % (y + 1)

            u = User(
                slug='teammember%d' % (y + 1)
            )

            if username is not None:
                u.username = username

            u.save()
            u.teams.add(t)
            u.save()
            t.save()
        # Before we go to the next team, increment start ID for member name
        user_global_id += num_members
    return o
