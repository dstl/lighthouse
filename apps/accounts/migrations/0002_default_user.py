# -*- coding: utf-8 -*-
# (c) Crown Owned Copyright, 2016. Dstl.

from __future__ import unicode_literals

from django.db import migrations


def create_lighthouse_user(apps, schema_editor):
    # We can't import models directly from code as they will eventually
    # be newer versions than this migration expects.
    User = apps.get_model('accounts', 'User')

    User.objects.create(
        userid='lighthouseuser',
        slug='lighthouseuser',
        name='Lighthouse User',
        best_way_to_contact='Do not contact me, I am a fake user.',
        best_way_to_find='Nowhere: I am not real.',
        is_active=False,
    )


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_lighthouse_user),
    ]
