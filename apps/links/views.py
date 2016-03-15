# (c) Crown Owned Copyright, 2016. Dstl.

import csv

from django import forms

# TODO — restore this next line and retire .mixins once we are back at django
#        1.9 or above
# from django.contrib.auth.mixins import LoginRequiredMixin
from .mixins import LoginRequiredMixin

from django.db.models import Count
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
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

from django.shortcuts import redirect
from django.core.urlresolvers import reverse

from .models import Link, LinkUsage
from apps.users.models import User


class LinkDetail(DetailView):
    model = Link


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


class LinkUsageAPI(DetailView):
    model = Link

    # TODO (probably)
    # - there is no authentication
    # - there is no way to discover link IDs
    # - there is no way to discover user slugs

    def get(self, request, *args, **kwargs):
        """ Return the usage stats as JSON """
        link = self.get_object()
        response = []
        for use in link.usage.all():
            response.append({
                'user': use.user.slug,
                'date': use.start,
            })
        return JsonResponse(response, safe=False)

    def post(self, request, *args, **kwargs):
        """ Add new usage stat """
        # user param is required
        if 'user' not in request.POST:
            return JsonResponse({'error': 'user required'}, status=400)

        # user must exist
        try:
            user = User.objects.get(slug=request.POST.get('user'))
        except User.DoesNotExist:
            return JsonResponse({'error': 'no such user'}, status=400)

        link = self.get_object()
        link.register_usage(user)
        return JsonResponse({'status': 'ok'}, status=201)


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


class LinkUpdate(LoginRequiredMixin, CategoriesFormMixin, UpdateView):
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
        context['total_links_in_db'] = Link.objects.count()
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
        writer.writerow(['Date', 'User', 'Tool'])
        for usage in link.usage.all():
            writer.writerow([
                usage.start.strftime("%Y-%m-%d %H:%M:%S"),
                usage.user,
                usage.link
            ])

        return response


class OverallLinkStats(ListView):
    template_name = 'links/link_overall_stats.html'

    def get_queryset(self):
        return Link.objects.annotate(Count('usage')).order_by('-usage__count')


class OverallLinkStatsCSV(View):
    def get(self, request, *args, **kwargs):
        date = timezone.now().strftime('%Y_%m_%d')
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = \
            'attachment; filename="lighthouse_full_%s.csv"' % date

        writer = csv.writer(response)
        writer.writerow(['Date', 'User', 'Tool'])
        for usage in LinkUsage.objects.all():
            writer.writerow([
                usage.start.strftime("%Y-%m-%d %H:%M:%S"),
                usage.user,
                usage.link
            ])

        return response
