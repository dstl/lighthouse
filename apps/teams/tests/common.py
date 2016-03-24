# (c) Crown Owned Copyright, 2016. Dstl.

from apps.organisations.models import Organisation
from apps.teams.models import Team
from apps.users.models import User


def create_team(name, num_members=0, usernames={}):
    o = Organisation(name="Organisation for %s" % name)
    o.save()
    t = Team(name=name, organisation=o)
    t.save()
    for x in range(0, num_members):
        if x in usernames.keys():
            username = usernames[x]
        else:
            username = 'Team Member %d' % (x + 1)

        u = User(
            slug='teammember%d' % (x + 1),
            original_slug='teammember%d' % (x + 1),
        )

        if username is not None:
            u.username = username

        u.save()
        u.teams.add(t)
        u.save()
        t.save()
    return t
