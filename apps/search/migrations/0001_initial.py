# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_auto_20160314_1659'),
    ]

    operations = [
        migrations.CreateModel(
            name='SearchQuery',
            fields=[
                ('id', models.AutoField(
                    auto_created=True,
                    serialize=False,
                    verbose_name='ID',
                    primary_key=True
                )),
                ('when', models.DateTimeField(auto_now_add=True)),
                ('results_length', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='SearchTerm',
            fields=[
                ('id', models.AutoField(
                    auto_created=True,
                    serialize=False,
                    verbose_name='ID',
                    primary_key=True
                )
                ),
                ('query', models.CharField(max_length=255, default=None)),
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
            field=models.ForeignKey(to='users.User'),
        ),
    ]
