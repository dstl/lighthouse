from django.core.urlresolvers import reverse
from django.db import models
from apps.users.models import User
from taggit.managers import TaggableManager


class Link(models.Model):
    name = models.CharField(max_length=256)
    description = models.TextField(null=True, blank=True)
    destination = models.URLField(max_length=2000, unique=True)
    owner = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        blank=True
    )
    categories = TaggableManager()

    def get_absolute_url(self):
        return reverse('link-detail', kwargs={'pk': self.pk})

    def __unicode__(self):
        return self.name
