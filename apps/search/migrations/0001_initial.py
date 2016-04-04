# -*- coding: utf-8 -*-
# (c) Crown Owned Copyright, 2016. Dstl.

from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SearchQuery',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID', primary_key=True,
                    auto_created=True, serialize=False)),
                ('when', models.DateTimeField(auto_now_add=True)),
                ('results_length', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='SearchTerm',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID', primary_key=True,
                    auto_created=True, serialize=False)),
                ('query', models.CharField(default=None, max_length=255)),
            ],
        ),
        migrations.AddField(
            model_name='searchquery',
            name='term',
            field=models.ForeignKey(to='search.SearchTerm'),
        ),
        migrations.AddField(
            model_name='searchquery',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
        ),
    ]
