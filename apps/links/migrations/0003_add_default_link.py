# -*- coding: utf-8 -*-
# (c) Crown Owned Copyright, 2016. Dstl.

from __future__ import unicode_literals

from django.db import migrations


def create_lighthouse_link(apps, schema_editor):
    # We can't import models directly from code as they will eventually
    # be newer versions than this migration expects.
    User = apps.get_model('accounts', 'User')
    Link = apps.get_model('links', 'Link')

    default_user = User.objects.get(pk=1)

    Link.objects.create(
        description=(
            'Web application for finding useful tools, '
            'data and techniques'
        ),
        destination='/',
        name='Lighthouse',
        owner=default_user,
    )


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_default_user'),
        ('links', '0002_linkusage_end'),
    ]

    operations = [
        migrations.RunPython(create_lighthouse_link),
    ]
