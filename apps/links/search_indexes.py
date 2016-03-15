# (c) Crown Owned Copyright, 2016. Dstl.

from haystack import indexes

from .models import Link


class LinkIndex(indexes.SearchIndex, indexes.Indexable):
    name = indexes.CharField(model_attr='name')
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        return Link
