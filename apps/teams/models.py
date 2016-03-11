# (c) Crown Owned Copyright, 2016. Dstl.
# apps/teams/models.py
from django.core.urlresolvers import reverse
from django.db import models
from apps.organisations.models import Organisation


class Team(models.Model):
    name = models.CharField(max_length=256, unique=True)
    organisation = models.ForeignKey(Organisation)

    class Meta:
        ordering = ["name"]

    @classmethod
    def with_most_members(cls):
        return Team.objects.all().annotate(
            count=models.Count('user')
        ).filter(count__gte=1).order_by('-count', 'name')

    def get_absolute_url(self):
        return reverse('team-detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.name

    def top_links(self):
        from apps.links.models import Link
        return Link.objects.filter(
            usage__user__in=self.user_set.all()
        ).annotate(
            linkusagecount=models.Count('usage')
        ).order_by('-linkusagecount', 'name')
