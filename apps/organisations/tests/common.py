# (c) Crown Owned Copyright, 2016. Dstl.

from testing import common
from testing.decorators import testing_depreceated


@testing_depreceated(common.create_organisation)
def create_organisation(name, num_teams=0, num_members=0, usernames={}):
    return common.create_organisation(name, num_teams, num_members, usernames)
