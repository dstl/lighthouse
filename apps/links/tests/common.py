# (c) Crown Owned Copyright, 2016. Dstl.
from testing import common
from testing.decorators import testing_depreceated


@testing_depreceated(common.generate_fake_links)
def generate_fake_links(owner, start=1, count=1, is_external=False):
    return common.generate_fake_links(owner, start, count, is_external)


@testing_depreceated(common.make_user)
def make_user(
        original_slug='user@0001.com',
        email='fake@dstl.gov.uk',
        name='Fake Fakerly'):
    return common.make_user(original_slug, email, name)


@testing_depreceated(common.login_user)
def login_user(owner, user):
    return common.login_user(owner, user)
