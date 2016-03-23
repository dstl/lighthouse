# -*- coding: utf-8 -*-
# (c) Crown Owned Copyright, 2016. Dstl.
from __future__ import unicode_literals
from django.db import migrations
from django.utils.text import slugify


def migrate_slug(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    User = apps.get_model("users", "User")
    for user in User.objects.all():
        user.original_slug = user.slug
        user.slug = slugify(user.slug)
        user.save()


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0004_user_original_slug"),
    ]

    operations = [
        migrations.RunPython(migrate_slug),
    ]
