# (c) Crown Owned Copyright, 2016. Dstl.
# apps/organisations/views.py
from django.views.generic import CreateView, DetailView, ListView
from django.core.urlresolvers import reverse
from .models import Organisation
from apps.teams.models import Team
from .forms import OrganisationForm
from apps.widgets.common import TopOrganisations, TopTeams


class OrganisationList(ListView):
    model = Organisation

    #   We're also going to jam the for on the list view page.
    def get_context_data(self, **kwargs):
        context = super(OrganisationList, self).get_context_data(**kwargs)

        context['show_more_teams_link'], context['top_teams'] = TopTeams()
        context['show_more_organisations_link'], \
            context['top_organisations'] = TopOrganisations()

        return context


class OrganisationCreate(CreateView):
    model = Organisation
    form_class = OrganisationForm

    def get_success_url(self):
        return reverse('organisation-list')


class OrganisationDetail(DetailView):
    model = Organisation

    def get_context_data(self, **kwargs):
        context = super(OrganisationDetail, self).get_context_data(**kwargs)
        context['teams'] = Team.objects.filter(
            organisation=context.get('organisation'))
        return context
