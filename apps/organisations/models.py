# (c) Crown Owned Copyright, 2016. Dstl.
# apps/organisations/models.py
from django.core.urlresolvers import reverse
from django.db import models


class Organisation(models.Model):
    name = models.CharField(max_length=256, unique=True)

    class Meta:
        ordering = ["name"]

    def get_absolute_url(self):
        return reverse('organisation-detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.name
