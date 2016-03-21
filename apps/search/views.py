from haystack.views import SearchView
from django.views.generic import ListView
from .models import SearchQuery, SearchTerm


class SearchStats(ListView):
    model = SearchQuery
    template_name = 'search/search_stats.html'

    def get_queryset(self):
        return SearchQuery.objects.order_by('-when')[:20]


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
