# (c) Crown Owned Copyright, 2016. Dstl.
# apps/organisations/models.py
from django.core.urlresolvers import reverse
from django.db import models


class Organisation(models.Model):
    name = models.CharField(max_length=256, unique=True)

    class Meta:
        ordering = ["name"]

    @classmethod
    def with_most_teams(cls):
        return Organisation.objects.all().annotate(
                count=models.Count('team')
            ).filter(count__gte=1).order_by('-count', 'name')

    def get_absolute_url(self):
        return reverse('organisation-detail', kwargs={'pk': self.pk})

    def __str__(self):
        return self.name

    def top_links(self):
        from apps.links.models import Link
        from apps.users.models import User

        all_organisation_users = User.objects.filter(
            teams__in=self.team_set.all()
        ).distinct()

        return Link.objects.filter(
            usage__user__in=all_organisation_users
        ).annotate(
            linkusagecount=models.Count('usage')
        ).order_by('-linkusagecount', 'name')
