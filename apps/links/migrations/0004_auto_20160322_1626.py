# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('links', '0003_auto_20160310_1042'),
    ]

    operations = [
        migrations.AddField(
            model_name='link',
            name='added',
            field=models.DateTimeField(null=True, auto_now_add=True),
        ),
        migrations.AlterField(
            model_name='linkusage',
            name='user',
            field=models.ForeignKey(to='users.User', related_name='usage'),
        ),
    ]
