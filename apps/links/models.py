# (c) Crown Owned Copyright, 2016. Dstl.

import json

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

    #   A somewhat loopy method of getting the top team usage for tools in
    #   the last 30 days. *Because* a user can be a member of more than one
    #   team, counting the usage per team isn't totally straight forwards.
    #   For example, we have two users A & B. A is a member of team1 & team2,
    #   while B is a member of team2 & team3.
    #   User A uses a tool 5 times and user B used a tool 7 times, then
    #   team1 will have 'used' the tool 5 times from user A,
    #   team3 will have 'used' the tool 7 times from user B,
    #   team2 will have 'used' the tool 12 times from users A + B.
    #   Sooooo.....
    def top_teams_thirty_days(self):
        #   The first thing we do is grab all the users who have used this
        #   tool in the last 30 days.
        users = self.top_users_thirty_days()

        #   Create an empty JSON stub to hold the values we want to manipulate.
        #   The reasons for using JSON rather than a dict object is that
        #   it's easier to add entries and check for their existance on a
        #   JSON object than a dict, which involves us invoking __setitem__
        #   and we want to avoid calling double underscore methods.
        teamsJSON = json.loads('{}')

        #   Loop thru the users...
        for user in users:
            #   and now look at all the teams the user belongs to
            for team in user.teams.all():

                #   if we already have the team in the teamsJSON then we can
                #   simple increment the number of times they've used the
                #   tool based on the user.
                if team.pk in teamsJSON:
                    teamsJSON[team.pk]['link_usage_count'] += \
                        user.link_usage_count
                else:
                    #   Otherwise we add the team.pk to the teamsJSON with
                    #   the value of a new empty JSON stub, which we use
                    #   to hold the team object and the link_usage_count
                    teamsJSON[team.pk] = json.loads('{}')
                    teamsJSON[team.pk]['team'] = team
                    teamsJSON[team.pk]['link_usage_count'] = \
                        user.link_usage_count

        #   Because the JSON object is *really* a dict object but with a nicer
        #   interface we can grab the values out (which strips off the keys
        #   we nolonger need)...
        teams = teamsJSON.values()
        #   ...and now we can just sort by the usage count.
        return sorted(
            teams,
            key=lambda o: (o['link_usage_count']),
            reverse=True
        )

    #   This does pretty much the same again as the function above
    #   (top_teams_thirty_days), but with the extra step that we only want
    #   to count each user once for an organisation.
    #   For example, user A may be a member of team 1 & 2, both teams are
    #   part of organisation 1. If user A uses tool 1, 5 times, then we
    #   don't want to count those 5 uses from user A coming from team 1, and
    #   then again from team 2.
    #   We are only going to count each user once for each organisation.
    def top_organisations_thirty_days(self):

        users = self.top_users_thirty_days()

        #   We are going to use two JSON objects, one to store the orgs and
        #   links data, and the other to act as a 'map' of users on an org
        #   so we can populate the 'map' when we 1st see a user in an org
        #   as to not count link usage for that user in that org a second time,
        #   (Because the user may be a member of more than 1 team in that org).
        #   We do this because there may be many many users in an org, and
        #   we want to keep the object that we finally sort and send to the
        #   template to be small as possible.
        orgsLinksJSON = json.loads('{}')
        orgsUserJSON = json.loads('{}')

        for user in users:
            #   and now look at all the teams the user belongs to
            for team in user.teams.all():
                #   If an entry for this organisation doesn't already exist
                #   in the orgsJSON then we need to add it.
                if team.organisation.pk not in orgsLinksJSON:
                    #   Create an empty JSON stubs, and populate them with
                    #   default values.
                    orgsLinksJSON[team.organisation.pk] = json.loads('{}')
                    orgsLinksJSON[team.organisation.pk]['organisation'] = \
                        team.organisation
                    orgsLinksJSON[team.organisation.pk]['link_usage_count'] = 0
                    #   Here is the user 'map'
                    orgsUserJSON[team.organisation.pk] = json.loads('{}')
                    orgsUserJSON[team.organisation.pk]['users'] = \
                        json.loads('{}')

                #   Now that we *know* we have at least a default JSON stub
                #   for this organisation, we can check to see if we have
                #   recorded the usage for this user in this organisation.
                #   If the user *doesn't* exists in the 'lookup' map of
                #   users, then we put them in and increment the usage count
                #   for the organisation
                if user.pk not in orgsUserJSON[team.organisation.pk]['users']:
                    orgsUserJSON[team.organisation.pk]['users'][user.pk] = True
                    orgsLinksJSON[team.organisation.pk]['link_usage_count'] \
                        += user.link_usage_count

        #   Phew, now we have all the orgs with total usage count, without
        #   duplicating usage from users being in more than one team that
        #   shares an org. Let's turn it back into a dict without the keys
        orgs = orgsLinksJSON.values()
        return sorted(
            orgs,
            key=lambda o: (o['link_usage_count']),
            reverse=True
        )

    def __str__(self):
        return self.name
