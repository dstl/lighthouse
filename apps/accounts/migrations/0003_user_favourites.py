# -*- coding: utf-8 -*-
# (c) Crown Owned Copyright, 2016. Dstl.

from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('links', '0004_add_lighthouse_api'),
        ('accounts', '0002_default_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='favourites',
            field=models.ManyToManyField(to='links.Link'),
        ),
    ]
