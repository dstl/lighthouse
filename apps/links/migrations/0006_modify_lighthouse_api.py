# -*- coding: utf-8 -*-
# (c) Crown Owned Copyright, 2016. Dstl.

from __future__ import unicode_literals

from django.db import migrations


def modify_lighthouse_api_link(apps, schema_editor):
    # We can't import models directly from code as they will eventually
    # be newer versions than this migration expects.
    Link = apps.get_model('links', 'Link')

    api_link = Link.objects.get(id=2)

    description = 'The API for this application.'
    description += '\n\nDocumentation for using the API can be found at '
    description += '[/api](/api).'

    api_link.description = description

    api_link.save()


class Migration(migrations.Migration):

    dependencies = [
        ('links', '0005_linkedit'),
    ]

    operations = [
        migrations.RunPython(modify_lighthouse_api_link),
    ]
