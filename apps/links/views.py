from django.views.generic import CreateView, DetailView

from .models import Link


class LinkDetail(DetailView):
    model = Link


class LinkCreate(CreateView):
    model = Link
    fields = ['name', 'description', 'destination']
