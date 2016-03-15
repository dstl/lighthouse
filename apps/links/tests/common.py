# (c) Crown Owned Copyright, 2016. Dstl.
from django.core.urlresolvers import reverse
from apps.links.models import Link
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


def make_user():
    user = User(
        slug='user0001com',
        original_slug='user@0001.com',
        username='Fake Fakerly',
        phone='555-2187',
        email='fake@dstl.gov.uk')
    user.save()
    return user


def login_user(owner, user):

    #   Log in as user
    form = owner.app.get(reverse('login-view')).form
    form['slug'] = 'user0001com'
    response = form.submit().follow()

    user_id = response.html.find(
            'span', attrs={'class': 'user_id'}
        ).attrs['data-slug']
    return (user_id == user.slug)
