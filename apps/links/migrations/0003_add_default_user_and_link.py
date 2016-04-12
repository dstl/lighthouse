# -*- coding: utf-8 -*-
# (c) Crown Owned Copyright, 2016. Dstl.

from __future__ import unicode_literals

from django.db import migrations


def create_lighthouse_user(apps, schema_editor):
    # We can't import the User model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    User = apps.get_model('accounts', 'User')
    Link = apps.get_model('links', 'Link')

    default_user = User(
        userid='lighthouseuser',
        name='Lighthouse User',
        slug='lighthouseuser',
        best_way_to_find='Nowhere: I am not real.',
        best_way_to_contact='Do not contact me, I am a fake user.',
    )

    default_user.save()

    description = 'Web application for finding useful'
    description += ' tools, data and techniques'

    lighthouse_link = Link()

    lighthouse_link.owner = default_user
    lighthouse_link.name = 'Lighthouse'
    lighthouse_link.description = description
    lighthouse_link.destination = '/'

    lighthouse_link.save()


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('links', '0002_linkusage_end'),
    ]

    operations = [
        migrations.RunPython(create_lighthouse_user),
    ]
