# (c) Crown Owned Copyright, 2016. Dstl.

from django.core.urlresolvers import reverse

from apps.links.models import Link
from apps.organisations.models import Organisation
from apps.teams.models import Team
from apps.users.models import User


def generate_fake_links(owner, start=1, count=1, is_external=False):
    for i in range(start, start + count):
        if is_external:
            url = "https://testsite%d.com" % i
        else:
            url = "https://testsite%d.dstl.gov.uk" % i
        link = Link(
            name="Test Tool %d" % i,
            description='How do you describe a tool like tool %d?' % i,
            destination=url,
            owner=owner,
            is_external=is_external
        )
        link.save()
        yield link


def make_user(
        original_slug='user@0001.com',
        email='fake@dstl.gov.uk',
        name='Fake Fakerly'):
    slug = original_slug.replace('@', '').replace('.', '')
    user = User(
        slug=slug,
        original_slug=original_slug,
        username=name,
        phone='555-2187',
        email=email)
    user.save()
    return user


def login_user(owner, user):
    #   Log in as user
    form = owner.app.get(reverse('login-view')).form
    form['slug'] = user.slug
    response = form.submit().follow()

    user_id = response.html.find(
            'span', attrs={'class': 'user_id'}
        ).attrs['data-slug']
    return (user_id == user.slug)


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
