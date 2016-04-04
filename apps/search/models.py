# (c) Crown Owned Copyright, 2016. Dstl.

from django.conf import settings
from django.db import models


class SearchTerm(models.Model):
    query = models.CharField(
        max_length=255,
        default=None
    )

    def __str__(self):
        return self.query


class SearchQuery(models.Model):
    term = models.ForeignKey(SearchTerm)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    when = models.DateTimeField(auto_now_add=True)
    results_length = models.IntegerField()
