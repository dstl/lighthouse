# (c) Crown Owned Copyright, 2016. Dstl.

from testing import common
from testing.decorators import testing_depreceated


@testing_depreceated(common.create_team)
def create_team(name, num_members=0, usernames={}):
    return common.create_team(name, num_members, usernames)
