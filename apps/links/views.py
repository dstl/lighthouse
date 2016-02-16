from django.views.generic import CreateView, DetailView, ListView, UpdateView
from taggit.models import Tag

from .models import Link


class LinkDetail(DetailView):
    model = Link


class LinkCreate(CreateView):
    model = Link
    # The fields will map to the form data names to use in the `name` fields.
    fields = ['name', 'description', 'destination', 'categories']

    def get_context_data(self, **kwargs):
        context = super(LinkCreate, self).get_context_data(**kwargs)
        tags = Tag.objects.all()
        context["existing_categories"] = tags
        return context

    # Using form_valid may not be the 'correct' way to do this
    def form_valid(self, form):
        form.instance.owner = self.request.user

        cleaned_categories_list = [
            category.strip(' ,') for
            category in
            form.data.getlist('categories') if (category.strip(' ,'))
        ]
        if (len(cleaned_categories_list) > 0):
            if (form.is_valid()):
                form.save()
                for category in cleaned_categories_list:
                    form.instance.categories.add(category)
                form.save()
        return super(LinkCreate, self).form_valid(form)


class LinkEdit(UpdateView):
    model = Link
    fields = ['name', 'description', 'destination', 'categories']

    def get_context_data(self, **kwargs):
        context = super(LinkEdit, self).get_context_data(**kwargs)
        return context


class LinkList(ListView):
    model = Link
    paginate_by = 5
