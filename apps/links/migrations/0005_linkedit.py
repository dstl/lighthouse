# -*- coding: utf-8 -*-
# (c) Crown Owned Copyright, 2016. Dstl.
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('links', '0004_add_lighthouse_api'),
    ]

    operations = [
        migrations.CreateModel(
            name='LinkEdit',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, verbose_name='ID', primary_key=True,
                    serialize=False)),
                ('date', models.DateTimeField(auto_now_add=True, null=True)),
                ('link', models.ForeignKey(
                    related_name='edits', to='links.Link')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
