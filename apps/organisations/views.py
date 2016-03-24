# (c) Crown Owned Copyright, 2016. Dstl.

from django.core.urlresolvers import reverse
from django.views.generic import CreateView, DetailView, ListView

from .forms import OrganisationForm
from .models import Organisation
from apps.access import LoginRequiredMixin
from apps.teams.models import Team


class OrganisationList(LoginRequiredMixin, ListView):
    model = Organisation
    paginate_by = 20

    #   We're also going to jam the for on the list view page.
    def get_context_data(self, **kwargs):
        context = super(OrganisationList, self).get_context_data(**kwargs)

        context['top_teams'] = Team.with_most_members()
        context['top_organisations'] = Organisation.with_most_teams()
        context['total_organisations_in_db'] = Organisation.objects.count()

        return context


class OrganisationCreate(LoginRequiredMixin, CreateView):
    model = Organisation
    form_class = OrganisationForm

    def get_success_url(self):
        return reverse('organisation-list')


class OrganisationDetail(LoginRequiredMixin, DetailView):
    model = Organisation

    def get_context_data(self, **kwargs):
        context = super(OrganisationDetail, self).get_context_data(**kwargs)
        context['teams'] = Team.objects.filter(
            organisation=context.get('organisation'))
        return context
