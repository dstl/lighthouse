# -*- coding: utf-8 -*-
# (c) Crown Owned Copyright, 2016. Dstl.
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_auto_20160314_1659'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'ordering': ['username', 'original_slug']},
        ),
    ]
