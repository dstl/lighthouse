# (c) Crown Owned Copyright, 2016. Dstl.

from haystack import indexes

from .models import Link


class SearchableBooleanField(indexes.CharField):
    def convert(self, value):
        if value:
            return 'external'
        else:
            return 'internal'


class LinkIndex(indexes.SearchIndex, indexes.Indexable):
    name = indexes.CharField(model_attr='name')
    categories = indexes.MultiValueField(indexed=True, stored=True)
    text = indexes.CharField(document=True, use_template=True)
    network_location = SearchableBooleanField(model_attr='is_external')

    def get_model(self):
        return Link

    def prepare_categories(self, link):
        return [categories.name for categories in link.categories.all()]
