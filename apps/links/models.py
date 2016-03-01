# (c) Crown Owned Copyright, 2016. Dstl.
from django.core.urlresolvers import reverse
from django.db import models
from apps.users.models import User
from taggit.managers import TaggableManager


class Link(models.Model):
    name = models.CharField(max_length=256)
    description = models.TextField(null=True, blank=True)
    destination = models.URLField(max_length=2000, unique=True)
    is_external = models.BooleanField(default=False, blank=False)
    owner = models.ForeignKey(
        User,
        on_delete=models.PROTECT
    )
    categories = TaggableManager(blank=True)

    def get_absolute_url(self):
        return reverse('link-detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.name
