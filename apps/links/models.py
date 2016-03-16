# (c) Crown Owned Copyright, 2016. Dstl.

from datetime import timedelta
from dateutil.relativedelta import relativedelta, MO

from django.core.urlresolvers import reverse
from django.db import models
from django.utils import timezone

from apps.users.models import User
from taggit.managers import TaggableManager


class LinkUsage(models.Model):
    link = models.ForeignKey('Link', related_name='usage')
    user = models.ForeignKey(User, related_name='usage')
    start = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return 'Usage of %s by %s at %s' % (self.link, self.user, self.start)


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

    def register_usage(self, user):
        LinkUsage.objects.create(link=self, user=user).save()

    def usage_today(self):
        """ All usage since midnight """
        today = timezone.now().replace(hour=0, minute=0, second=0)
        return self.usage.filter(start__gt=today).count()

    def usage_this_week(self):
        """ All usage since midnight on Monday """
        today = timezone.now().replace(hour=0, minute=0, second=0)
        last_monday = today + relativedelta(weekday=MO(-1))
        return self.usage.filter(start__gt=last_monday).count()

    def usage_past_seven_days(self):
        """ All usage in the past seven days """
        today = timezone.now().replace(hour=0, minute=0, second=0)
        week_ago = today - timedelta(days=7)
        return self.usage.filter(start__gt=week_ago).count()

    def usage_this_month(self):
        """ All usage since midnight on the first of the month """
        first_of_month = timezone.now().replace(
            day=1, hour=0, minute=0, second=0)
        return self.usage.filter(start__gt=first_of_month).count()

    def usage_past_thirty_days(self):
        """ All usage in the past thirty days (approximately 'a month') """
        today = timezone.now().replace(hour=0, minute=0, second=0)
        month_ago = today - timedelta(days=30)
        return self.usage.filter(start__gt=month_ago).count()

    def usage_total(self):
        """ All usage ever """
        return self.usage.count()

    def top_users_thirty_days(self):
        today = timezone.now().replace(hour=0, minute=0, second=0)
        month_ago = today - timedelta(days=30)
        return User.objects.filter(
            usage__link=self,
            usage__start__gt=month_ago
        ).annotate(
            link_usage_count=models.Count('usage')
        ).order_by('-link_usage_count', 'slug')

    def __str__(self):
        return self.name
