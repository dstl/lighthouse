# apps/teams/views.py
from django.views.generic import CreateView, DetailView, ListView
from django.core.urlresolvers import reverse

from .models import Team
from .forms import TeamForm


class TeamList(ListView):
    model = Team


class TeamCreate(CreateView):
    model = Team
    form_class = TeamForm

    def get_success_url(self):
        return reverse('team-list')


class TeamDetail(DetailView):
    model = Team
