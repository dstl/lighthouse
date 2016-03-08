# (c) Crown Owned Copyright, 2016. Dstl.
# apps/users/views.py
from django.http import HttpResponseRedirect
from django.views.generic import DetailView, ListView, UpdateView
from django.core.urlresolvers import reverse
from django.db import models
from .models import User
from apps.teams.models import Team
from apps.organisations.models import Organisation


class UserDetail(DetailView):
    model = User


class UserUpdateProfile(UpdateView):
    model = User
    fields = [
                'username',
                'best_way_to_find',
                'best_way_to_contact',
                'phone',
                'email'
            ]
    template_name = 'users/user_details_form.html'

    def get_context_data(self, **kwargs):
        context = super(UserUpdateProfile, self).get_context_data(**kwargs)
        if (
            self.request.user.username is None or
            self.request.user.username == ''
        ):
            context['show_username_alert'] = True
        else:
            if (
                self.request.user.best_way_to_find is None or
                self.request.user.best_way_to_find == '' or
                self.request.user.best_way_to_contact is None or
                self.request.user.best_way_to_contact == '' or
                self.request.user.phone is None or
                self.request.user.phone == '' or
                self.request.user.email is None or
                self.request.user.email == ''
            ):
                context['show_extra_details_alert'] = True

        #   We want to grab all the teams so we can display a bunch of
        #   checkboxes allowing the user to join those teams
        if self.request.user.is_authenticated():
            teams = Team.objects.all()
            for team in teams:
                team.checked = False
                for us in self.request.user.teams.all():
                    if team.id == us.id:
                        team.checked = True

            context['teams'] = teams

        return context

    #   Once we've updated the details, go to user profile page
    def get_success_url(self):
        return reverse('user-detail', kwargs={'slug': self.request.user.slug})

    #   Only save the data if the user details match who we currently are
    #   TODO: Don't even show this page if the user slug doesn't match
    def form_valid(self, form):
        userDetails = form.save(commit=False)
        if userDetails.id == self.request.user.id:

            #   Now we need to dump all the current links to teams and
            #   then add them all back in.
            userDetails.teams.clear()
            for team in form.data.getlist('team'):
                userDetails.teams.add(int(team))
            userDetails.save()

        return HttpResponseRedirect(self.get_success_url())


class UserList(ListView):
    model = User

    def get_context_data(self, **kwargs):
        context = super(UserList, self).get_context_data(**kwargs)

        #   Get the 1st 10 teams ranked by number of members
        teams = Team.objects.all().annotate(count=models.Count('user'))
        context['show_more_teams_link'] = len(teams) > 20
        context['teams'] = teams.order_by('-count', 'name')[:20]

        #   Get the 1st 10 organisations ranked by number of teams
        organisations = Organisation.objects.all().annotate(
            count=models.Count('team')
        )
        context['show_more_organisations_link'] = len(organisations) > 20
        context['organisations'] = organisations.order_by(
            '-count', 'name')[:20]

        return context
