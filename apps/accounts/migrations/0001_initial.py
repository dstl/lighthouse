# -*- coding: utf-8 -*-
# (c) Crown Owned Copyright, 2016. Dstl.

from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
        ('teams', '0002_auto_20160301_1616'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(
                    primary_key=True, auto_created=True,
                    verbose_name='ID', serialize=False)),
                ('password', models.CharField(
                    max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(
                    null=True, blank=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(
                    help_text='Designates that this user has all permissions '
                    'without explicitly assigning them.',
                    default=False, verbose_name='superuser status')),
                ('userid', models.CharField(unique=True, max_length=256)),
                ('slug', models.SlugField(unique=True, max_length=256)),
                ('name', models.CharField(blank=True, max_length=512)),
                ('date_joined', models.DateTimeField(
                    default=django.utils.timezone.now)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('best_way_to_find', models.CharField(
                    default='', blank=True, max_length=1024)),
                ('best_way_to_contact', models.CharField(
                    default='', blank=True, max_length=1024)),
                ('phone', models.CharField(
                    default='', blank=True, max_length=256)),
                ('email', models.CharField(
                    default='', blank=True, max_length=256)),
                ('groups', models.ManyToManyField(
                    related_name='user_set', to='auth.Group',
                    related_query_name='user',
                    verbose_name='groups', help_text='The groups this user '
                    'belongs to. A user will get all permissions granted '
                    'to each of their groups.',
                    blank=True)),
                ('teams', models.ManyToManyField(to='teams.Team')),
                ('user_permissions', models.ManyToManyField(
                    related_name='user_set', to='auth.Permission',
                    related_query_name='user',
                    verbose_name='user permissions',
                    help_text='Specific permissions for this user.',
                    blank=True)),
            ],
            options={
                'ordering': ['name', 'userid'],
            },
        ),
    ]
