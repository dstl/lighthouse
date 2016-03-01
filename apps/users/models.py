# (c) Crown Owned Copyright, 2016. Dstl.
# apps/users/models.py
from django.core.urlresolvers import reverse
from django.db import models


class User(models.Model):
    slug = models.SlugField(max_length=256, unique=True)
    username = models.CharField(max_length=256, blank=True, null=True)
    best_way_to_find = models.CharField(max_length=1024, blank=True, null=True)
    best_way_to_contact = models.CharField(
        max_length=1024,
        blank=True,
        null=True)
    phone = models.CharField(max_length=256, blank=True, null=True)
    email = models.CharField(max_length=256, blank=True, null=True)
    last_login = models.DateTimeField(blank=True, null=True)

    def get_absolute_url(self):
        return reverse('user-detail', kwargs={'slug': self.slug})

    def __unicode__(self):
        return self.slug

    def __str__(self):
        return self.slug
