from django.views.generic import CreateView, DetailView, ListView

from .models import Link


class LinkDetail(DetailView):
    model = Link


class LinkCreate(CreateView):
    model = Link
    # The fields will map to the form data names to use in the `name` fields.
    fields = ['name', 'description', 'destination']


class LinkList(ListView):
    model = Link
    paginate_by = 5
