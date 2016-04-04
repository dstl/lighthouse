# -*- coding: utf-8 -*-
# (c) Crown Owned Copyright, 2016. Dstl.

from __future__ import unicode_literals

from django.db import migrations, models
import taggit.managers
from django.conf import settings
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('taggit', '0002_auto_20150616_2121'),
    ]

    operations = [
        migrations.CreateModel(
            name='Link',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID', primary_key=True,
                    auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=256)),
                ('description', models.TextField(blank=True, null=True)),
                ('destination', models.URLField(
                    max_length=2000, unique=True)),
                ('is_external', models.BooleanField(default=False)),
                ('added', models.DateTimeField(null=True, auto_now_add=True)),
                ('categories', taggit.managers.TaggableManager(
                    blank=True,
                    verbose_name='Tags',
                    to='taggit.Tag',
                    help_text='A comma-separated list of tags.',
                    through='taggit.TaggedItem',
                )),
                ('owner', models.ForeignKey(
                    on_delete=django.db.models.deletion.PROTECT,
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
        ),
        migrations.CreateModel(
            name='LinkUsage',
            fields=[
                ('id', models.AutoField(
                    verbose_name='ID', primary_key=True,
                    auto_created=True, serialize=False)),
                ('start', models.DateTimeField(auto_now_add=True)),
                ('link', models.ForeignKey(
                    to='links.Link', related_name='usage')),
                ('user', models.ForeignKey(
                    to=settings.AUTH_USER_MODEL,
                    related_name='usage')),
            ],
        ),
    ]
