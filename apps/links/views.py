# (c) Crown Owned Copyright, 2016. Dstl.

import csv

from django import forms
from django.core.urlresolvers import reverse
from django.db.models import Count
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.text import slugify
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    UpdateView,
    View,
)

from taggit.models import Tag

from .models import Link, LinkUsage, LinkEdit
from apps.access import LoginRequiredMixin

from haystack.inputs import AutoQuery
from haystack.query import SearchQuerySet

from apps.search.models import SearchQuery, SearchTerm


class LinkDetail(DetailView):
    model = Link

    def get_context_data(self, **kwargs):
        context = super(LinkDetail, self).get_context_data(**kwargs)

        if self.request.user.is_authenticated():
            is_fav = self.request.user.favourites.filter(
                id=self.object.id
            ).exists()
            context['favourite'] = is_fav

        context['not_lighthouse_link'] = self.object.id not in [1, 2]

        return context


class LinkRedirect(DetailView):
    model = Link

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.is_external and request.GET.get('redirect') is None:
            return redirect(
                reverse('link-interstitial', kwargs={'pk': self.object.pk})
            )

        # if request.user is not None:
        self.object.register_usage(request.user)

        return redirect(self.object.destination)


class LinkInterstitial(DetailView):
    model = Link
    template_name_suffix = '_interstitial'


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

    def clean(self):
        cleaned_data = super(CategoriesFormMixin, self).clean()

        if not self.request.user.is_authenticated():
            raise forms.ValidationError(
                "You must be logged in to create a link"
            )

        return cleaned_data

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


class LinkCreate(LoginRequiredMixin, CategoriesFormMixin, CreateView):
    model = Link
    fields = [
        'name', 'description', 'destination', 'is_external', 'categories'
    ]

    def get_context_data(self, **kwargs):
        context = super(LinkCreate, self).get_context_data(**kwargs)
        context['not_lighthouse_link'] = True

        return context


class LinkUpdate(LoginRequiredMixin, CategoriesFormMixin, UpdateView):
    model = Link
    fields = [
        'name', 'description', 'destination', 'is_external', 'categories'
    ]

    def get_context_data(self, **kwargs):
        context = super(LinkUpdate, self).get_context_data(**kwargs)
        context['not_lighthouse_link'] = self.object.pk not in [1, 2]

        return context

    def form_valid(self, form):
        original_link = self.get_object()
        form_valid = super(LinkUpdate, self).form_valid(form)

        if form_valid:
            link = self.get_object()
            link.owner = original_link.owner
            link.save()
            LinkEdit.objects.create(
                link=self.object,
                user=self.request.user
            )

        return form_valid


class LinkList(ListView):
    model = Link
    paginate_by = 5
    template_name = 'links/link_list.html'

    def has_query(self):
        return 'q' in self.request.GET and len(self.request.GET['q']) > 0

    def has_categories(self):
        return 'categories' in self.request.GET

    def external_only(self):
        types = self.request.GET.getlist('types', [])
        if type(types) == str:
            types = [types]
        return 'internal' not in types and 'external' in types

    def internal_only(self):
        types = self.request.GET.getlist('types', [])
        if type(types) == str:
            types = [types]
        return 'internal' in types and 'external' not in types

    def get_queryset(self):
        queryset = super(LinkList, self).get_queryset().order_by('-added')
        not_on_page = 'page' not in self.request.GET

        if self.has_query():
            queryset = SearchQuerySet().filter(
                content=AutoQuery(self.request.GET['q']),
            ).filter_or(
                categories=AutoQuery(self.request.GET['q'])
            ).filter_or(
                network_location=AutoQuery(self.request.GET['q'])
            )

        if self.has_categories():
            categories_to_filter = dict(self.request.GET)['categories']
            if type(categories_to_filter) == str:
                categories_to_filter = [categories_to_filter]
            if self.has_query():
                queryset = queryset.models(Link).filter(
                    categories__in=categories_to_filter
                )
            else:
                # At this point, the queryset should already be ordered because
                # of the original get_queryset call at the beginning of this
                # function.
                queryset = queryset.filter(
                    categories__name__in=categories_to_filter
                ).distinct()

        if self.external_only() or self.internal_only():
            if self.has_query():
                queryset = queryset.models(Link).exclude(
                    is_external=self.internal_only()
                )
            else:
                # At this point, the queryset should already be ordered because
                # of the original get_queryset call at the beginning of this
                # function.
                queryset = queryset.exclude(
                    is_external=self.internal_only()
                ).distinct()

        if self.has_query() and not self.has_categories() and not_on_page:
            # At this point the queryset is a list of SearchResult objects, all
            # of them. So, the length is accurate. By the time it reaches
            # context, it won't be.
            st, created = SearchTerm.objects.get_or_create(
                query=self.request.GET.get('q')
            )
            sq = SearchQuery()
            sq.term = st
            sq.results_length = len(queryset)
            sq.user = self.request.user
            sq.save()

        return queryset

    def get_context_data(self, **kwargs):
        context = super(LinkList, self).get_context_data(**kwargs)
        querystrings = []
        if 'categories' in self.request.GET:
            categories_to_filter = dict(self.request.GET)['categories']
            if type(categories_to_filter) == str:
                categories_to_filter = [categories_to_filter]
        else:
            categories_to_filter = []

        querystrings = ['categories=%s' % c for c in categories_to_filter]

        # At this point the context contains object_list which is either a list
        # of SearchResult objects or Link objects
        types_to_filter = self.request.GET.getlist('types', [])

        querystrings += ['types=%s' % t for t in types_to_filter]

        if self.has_query():
            context['query'] = self.request.GET['q']
            context['object_list'] = [result.object for
                                      result in
                                      context['object_list']]
            querystrings += ['q=%s' % self.request.GET['q']]
        context['categories'] = Tag.objects.all()
        context['filtered_categories'] = categories_to_filter
        context['filtered_types'] = types_to_filter
        context['total_links_in_db'] = Link.objects.count()

        context['extra_query_strings'] = '&'.join(querystrings)

        return context


class LinkStats(DetailView):
    model = Link
    template_name_suffix = '_stats'


class LinkStatsCSV(DetailView):
    model = Link

    def get(self, request, *args, **kwargs):
        link = self.get_object()
        date = timezone.now().strftime('%Y_%m_%d')
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = \
            'attachment; filename="lighthouse_%s_%s.csv"' % (
                slugify(link.name),
                date
            )

        writer = csv.writer(response)
        writer.writerow(['Date', 'Duration', 'User', 'Tool'])
        for usage in link.usage.all():
            writer.writerow([
                usage.start.strftime("%Y-%m-%d %H:%M:%S"),
                usage.duration,
                usage.user.userid,
                usage.link
            ])

        return response


class OverallLinkStats(ListView):
    template_name = 'links/link_overall_stats.html'

    def get_queryset(self):
        return sorted(
            Link.objects.annotate(Count('usage')),
            key=lambda o: (o.usage_past_thirty_days()),
            reverse=True
        )


class OverallLinkStatsCSV(View):
    def get(self, request, *args, **kwargs):
        date = timezone.now().strftime('%Y_%m_%d')
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = \
            'attachment; filename="lighthouse_full_%s.csv"' % date

        writer = csv.writer(response)
        writer.writerow(['Date', 'Duration', 'User', 'Tool'])
        for usage in LinkUsage.objects.all():
            writer.writerow([
                usage.start.strftime("%Y-%m-%d %H:%M:%S"),
                usage.duration,
                usage.user.userid,
                usage.link
            ])

        return response
