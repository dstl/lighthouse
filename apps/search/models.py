# (c) Crown Owned Copyright, 2016. Dstl.
from django.db import models
from apps.users.models import User


class SearchTerm(models.Model):
    query = models.CharField(
        max_length=255,
        default=None
    )

    def __str__(self):
        return self.query


class SearchQuery(models.Model):
    term = models.ForeignKey(SearchTerm)
    user = models.ForeignKey(User)
    when = models.DateTimeField(auto_now_add=True)
    results_length = models.IntegerField()
