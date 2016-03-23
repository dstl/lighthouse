# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('links', '0003_auto_20160310_1042'),
    ]

    operations = [
        migrations.AlterField(
            model_name='linkusage',
            name='user',
            field=models.ForeignKey(related_name='usage', to='users.User'),
        ),
    ]
