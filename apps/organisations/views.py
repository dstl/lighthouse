# (c) Crown Owned Copyright, 2016. Dstl.
# apps/organisations/views.py
from django.views.generic import CreateView, DetailView, ListView
from django.core.urlresolvers import reverse

from .models import Organisation
from apps.teams.models import Team
from .forms import OrganisationForm


class OrganisationList(ListView):
    model = Organisation


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
