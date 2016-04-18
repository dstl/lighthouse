# -*- coding: utf-8 -*-
# (c) Crown Owned Copyright, 2016. Dstl.

from __future__ import unicode_literals

from django.db import migrations


def create_lighthouse_api_link(apps, schema_editor):
    # We can't import models directly from code as they will eventually
    # be newer versions than this migration expects.
    User = apps.get_model('accounts', 'User')
    Link = apps.get_model('links', 'Link')

    default_user = User.objects.get(userid='lighthouseuser')

    Link.objects.create(
        description='The API for this application.',
        destination='/api/',
        name='Lighthouse API',
        owner=default_user,
    )


class Migration(migrations.Migration):

    dependencies = [
        ('links', '0003_add_default_link'),
    ]

    operations = [
        migrations.RunPython(create_lighthouse_api_link),
    ]
