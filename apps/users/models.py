from django.core.urlresolvers import reverse
from django.db import models


class User(models.Model):
    fullName = models.CharField(max_length=256)
    phone = models.CharField(max_length=256)
    email = models.CharField(max_length=256)

    def get_absolute_url(self):
        return reverse('user-detail', kwargs={'pk': self.pk})

    def __unicode__(self):
        return self.name
