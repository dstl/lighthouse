# apps/organisations/views.py
from django.views.generic import CreateView, DetailView, ListView
from django.core.urlresolvers import reverse

from .models import Organisation
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
