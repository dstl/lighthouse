# (c) Crown Owned Copyright, 2016. Dstl.

from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.shortcuts import redirect
from django.views.generic import CreateView, DetailView, ListView
from django.views.generic.base import TemplateView

from .forms import TeamForm
from .models import Team
from apps.access import LoginRequiredMixin
from apps.organisations.models import Organisation


class TeamList(LoginRequiredMixin, ListView):
    model = Team
    paginate_by = 20

    #   We're also going to jam the for on the list view page.
    def get_context_data(self, **kwargs):
        context = super(TeamList, self).get_context_data(**kwargs)
        context['form'] = TeamForm

        context['top_teams'] = Team.with_most_members()
        context['top_organisations'] = Organisation.with_most_teams()
        context['total_teams_in_db'] = Team.objects.count()

        return context


class TeamCreate(LoginRequiredMixin, CreateView):
    model = Team
    form_class = TeamForm

    def get_context_data(self, **kwargs):
        context = super(TeamCreate, self).get_context_data(**kwargs)

        if 'org_id' in self.kwargs:
            org_id = int(self.kwargs['org_id'])
            context['organisation'] = Organisation.objects.get(id=org_id)

        return context

    def get_success_url(self):
        if 'org_id' in self.kwargs:
            org_id = int(self.kwargs['org_id'])
            return reverse('organisation-detail', kwargs={"pk": org_id})

        return reverse('team-list')


class TeamDetail(LoginRequiredMixin, DetailView):
    model = Team

    def get_context_data(self, **kwargs):
        context = super(TeamDetail, self).get_context_data(**kwargs)

        #   Check to see if this team exists in this user's list of
        #   team membership. True if the array returned by the self.
        #   TODO: make this code slightly more polite rather than just
        #   depending on an error being thrown.
        try:
            self.request.user.teams.get(pk=kwargs.get('object').pk)
            context['team_member'] = True
        except:
            context['team_member'] = False
        return context


class TeamJoin(LoginRequiredMixin, TemplateView):

    def post(self, request, *args, **kwargs):

        #   If we are not logged in, send the user to the login page
        if not self.request.user.is_authenticated():
            return redirect(reverse('home'))

        #   Grab the id of the user and team we are attempting to join
        team_id = kwargs.get('pk')

        #   Make sure the team exists, and that we haven't been lied
        #   to with the URL
        team = Team.objects.filter(pk=team_id)
        check_team = team.exists()
        if check_team is False:
            return redirect(reverse('team-list'))

        #   Try and add the team to the user
        try:
            request.user.teams.add(team_id)
        except IntegrityError:
            return redirect(reverse('team-detail', kwargs={'pk': team_id}))

        return redirect(reverse('team-detail', kwargs={'pk': team_id}))


class TeamLeave(LoginRequiredMixin, TemplateView):

    def post(self, request, *args, **kwargs):

        #   If we are not logged in, send the user to the login page
        if not self.request.user.is_authenticated():
            return redirect(reverse('home'))

        #   Grab the id of the user and team we are attempting to join
        team_id = kwargs.get('pk')

        #   Make sure the team exists, and that we haven't been lied
        #   to with the URL
        team = Team.objects.filter(pk=team_id)
        check_team = team.exists()
        if check_team is False:
            return redirect(reverse('team-list'))

        #   Try and remove the team to the user
        try:
            request.user.teams.remove(team_id)
        except IntegrityError:
            return redirect(reverse('team-detail', kwargs={'pk': team_id}))

        return redirect(reverse('team-detail', kwargs={'pk': team_id}))
