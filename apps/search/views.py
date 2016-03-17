from haystack.views import SearchView
from django.views.generic import DetailView
from .models import SearchQuery, SearchTerm


class SearchStats(DetailView):
    model = SearchQuery
    template_name_suffix = '_stats'


def search(request):
    view = SearchView()
    response = view(request)

    if 'page' not in request.GET:
        st, created = SearchTerm.objects.get_or_create(
            query=request.GET['q']
        )
        sq = SearchQuery()
        sq.term = st
        sq.results_length = len(view.get_results())
        sq.user = request.user
        sq.save()

    return response
