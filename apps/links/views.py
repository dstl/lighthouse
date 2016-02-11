from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .models import Link


class LinkDetail(DetailView):
    model = Link


class LinkCreate(CreateView):
    model = Link
    # The fields will map to the form data names to use in the `name` fields.
    fields = ['name', 'description', 'destination']


class LinkEdit(UpdateView):
    model = Link
    fields = ['name', 'description', 'destination']

    def get_context_data(self, **kwargs):

        context = super(LinkEdit, self).get_context_data(**kwargs)

        return context


class LinkList(ListView):
    model = Link
    paginate_by = 5
