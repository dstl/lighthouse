# apps/organisations/models.py
from django.core.urlresolvers import reverse
from django.db import models


class Organisation(models.Model):
    name = models.CharField(max_length=256, unique=True)

    def get_absolute_url(self):
        return reverse('organisation-detail', kwargs={'pk': self.pk})

    def __unicode__(self):
        return self.name

    def __str__(self):
        return self.name
