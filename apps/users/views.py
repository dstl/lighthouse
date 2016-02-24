# apps/users/views.py
from django.views.generic import CreateView, DetailView, ListView, TemplateView
from django.core.urlresolvers import reverse

from .models import User, Organisation, Team
from .forms import TeamForm, OrganisationForm

"""
    The user is doing a lot of work, and we are keeping it all in this one
    file, 'cause they are all connected. We may break them out at some point.
    Anyway, here's the stuff that handles the views for...
    Users, Team, Organsations.

"""


###############################################################################
#
#   USERS
#
class UserDetail(DetailView):
    model = User


class UserCreate(CreateView):
    model = User
    fields = ['fullName', 'phone', 'email']


class UserList(ListView):
    model = User
    paginate_by = 5


class WhoAmI(TemplateView):
    template_name = 'user_page.html'

    def get_context_data(self, **kwargs):
        context = super(WhoAmI, self).get_context_data(**kwargs)
        return context


###############################################################################
#
#   TEAMS
#
class TeamList(ListView):
    model = Team


class TeamCreate(CreateView):
    model = Team
    form_class = TeamForm

    def get_success_url(self):
        return reverse('team-list')


class TeamDetail(DetailView):
    model = Team


###############################################################################
#
#   ORGANISATIONS
#
class OrganisationList(ListView):
    model = Organisation


class OrganisationCreate(CreateView):
    model = Organisation
    form_class = OrganisationForm

    def get_success_url(self):
        return reverse('organisation-list')


class OrganisationDetail(DetailView):
    model = Organisation
