# (c) Crown Owned Copyright, 2016. Dstl.
from django.http import HttpResponseRedirect
from django.views.generic import CreateView, DetailView, ListView, UpdateView
from taggit.models import Tag

from .models import Link


class LinkDetail(DetailView):
    model = Link


class LinkRedirect(DetailView):
    model = Link
    template_name_suffix = '_redirect'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.is_external:
            context = self.get_context_data(object=self.object)
            return self.render_to_response(context)
        else:
            return HttpResponseRedirect(self.object.destination)


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
    fields = [
        'name', 'description', 'destination', 'is_external', 'categories'
    ]


class LinkUpdate(CategoriesFormMixin, UpdateView):
    model = Link
    fields = [
        'name', 'description', 'destination', 'is_external', 'categories'
    ]


class LinkList(ListView):
    model = Link
    paginate_by = 5

    def get_queryset(self):
        qs = super(LinkList, self).get_queryset().order_by('id')
        if 'categories' in self.request.GET:
            categories_to_filter = dict(self.request.GET)['categories']
            if type(categories_to_filter) == str:
                categories_to_filter = [categories_to_filter]
            qs = Link.objects.filter(
                categories__name__in=categories_to_filter
            ).order_by('id').distinct()

        if 'types' in self.request.GET:
            types_to_filter = self.request.GET.getlist('types')
            if type(types_to_filter) == str:
                types_to_filter = [types_to_filter]
            if ('internal' in types_to_filter and
                    'external' not in types_to_filter):
                qs = qs.exclude(is_external=True)
            elif ('internal' not in types_to_filter and
                    'external' in types_to_filter):
                qs = qs.exclude(is_external=False)

        qs = qs.reverse()
        return qs

    def get_context_data(self, **kwargs):
        if 'categories' in self.request.GET:
            categories_to_filter = dict(self.request.GET)['categories']
            if type(categories_to_filter) == str:
                categories_to_filter = [categories_to_filter]
        else:
            categories_to_filter = []

        types_to_filter = self.request.GET.getlist('types', [])

        context = super(LinkList, self).get_context_data(**kwargs)
        context['categories'] = Tag.objects.all()
        context['filtered_categories'] = categories_to_filter
        context['filtered_types'] = types_to_filter
        return context
