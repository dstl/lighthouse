import csv

from haystack.views import SearchView
from django.views.generic import ListView, View
from django.http import HttpResponse
from django.utils import timezone
from .models import SearchQuery, SearchTerm


class SearchStats(ListView):
    model = SearchQuery
    template_name = 'search/search_stats.html'

    def get_queryset(self):
        return SearchQuery.objects.order_by('-when')[:20]


class SearchStatsCSV(View):
    def get(self, request, *args, **kwargs):
        response = HttpResponse(content_type='text/csv')
        date = timezone.now().strftime('%Y_%m_%d')
        response['Content-Disposition'] = \
            'attachment; filename="lighthouse_search_full_%s.csv"' % date

        writer = csv.writer(response)
        writer.writerow(['Date', 'User', 'Term', 'Number of Results'])
        for query in SearchQuery.objects.all():
            writer.writerow([
                query.when.strftime("%Y-%m-%d %H:%M:%S"),
                query.user,
                query.term,
                query.results_length
            ])

        return response


def search(request):
    view = SearchView()
    response = view(request)

    if 'page' not in request.GET:
        st, created = SearchTerm.objects.get_or_create(
            query=request.GET.get('q')
        )
        sq = SearchQuery()
        sq.term = st
        sq.results_length = len(view.get_results())
        sq.user = request.user
        sq.save()

    return response
