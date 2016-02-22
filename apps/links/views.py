from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.generic import CreateView, DetailView, ListView, UpdateView
from taggit.models import Tag

from .models import Link
from .forms import LinkForm


class LinkDetail(DetailView):
    model = Link


def clean_categories(provided_categories):
    cleaned_categories = []
    for cat in [cat.strip(' ,') for cat in provided_categories]:
        # Check first if there's anything left, and if there is,
        # determine if it's one of the checklisted items or from the
        # text box (indicated by comma-separation)
        if cat:
            if (type(cat.split(',') is list)):
                cleaned_categories.extend(
                    [new_cat.strip(' ,') for new_cat in cat.split(',')]
                )
            else:
                cleaned_categories.add(cat)
    return cleaned_categories


class CategoriesFormMixin(object):
    def get_context_data(self, **kwargs):
        context = super(CategoriesFormMixin, self).get_context_data(**kwargs)
        context['existing_categories'] = Tag.objects.all()
        return context

    def form_valid(self, form):
        form.instance.owner = self.request.user
        # first save gets us the object in the database (when creating a new
        # link), as you can't apply tags without a primary key
        link = form.save()
        provided_categories = form.data.getlist('categories')
        cleaned_categories = clean_categories(provided_categories)
        form.instance.categories.set(*cleaned_categories)
        link.save()
        self.object = link
        return HttpResponseRedirect(self.get_success_url())


class LinkCreate(CategoriesFormMixin, CreateView):
    model = Link
    fields = ['name', 'description', 'destination', 'is_external', 'categories']


class LinkUpdate(CategoriesFormMixin, UpdateView):
    model = Link
    fields = ['name', 'description', 'destination', 'is_external', 'categories']


class LinkList(ListView):
    model = Link
    paginate_by = 5
