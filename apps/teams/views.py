# (c) Crown Owned Copyright, 2016. Dstl.
# apps/teams/views.py
from django.views.generic import CreateView, DetailView, ListView
from django.core.urlresolvers import reverse

from .models import Team
from .forms import TeamForm


class TeamList(ListView):
    model = Team

    #   We're also going to jam the for on the list view page.
    def get_context_data(self, **kwargs):
        context = super(TeamList, self).get_context_data(**kwargs)
        context['form'] = TeamForm
        return context


class TeamCreate(CreateView):
    model = Team
    form_class = TeamForm

    def get_success_url(self):
        return reverse('team-list')


class TeamDetail(DetailView):
    model = Team
