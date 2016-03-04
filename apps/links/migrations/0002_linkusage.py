# -*- coding: utf-8 -*-
# (c) Crown Owned Copyright, 2016. Dstl.
# Generated by Django 1.9.1 on 2016-03-01 15:50

from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
        ('links', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LinkUsage',
            fields=[
                ('id', models.AutoField(
                    auto_created=True, primary_key=True, serialize=False,
                    verbose_name='ID')),
                ('start', models.DateTimeField(auto_now_add=True)),
                ('link', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='links.Link')),
                ('user', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    to='users.User')),
            ],
        ),
    ]