# (c) Crown Owned Copyright, 2016. Dstl.

import re

from haystack import indexes
from whoosh.lang.morph_en import variations

from .models import Link


class SearchableBooleanField(indexes.CharField):
    def convert(self, value):
        if value:
            return 'external'
        else:
            return 'internal'


class VariationCharField(indexes.CharField):
    def prepare(self, obj):
        res = super(VariationCharField, self).prepare(obj)
        all_terms = re.findall("[\w]+", res, re.IGNORECASE)
        all_variations = [' '.join(variations(term.lower())) for
                          term in all_terms]

        for variation in all_variations:
            res += '\n%s' % variation

        return res


class LinkIndex(indexes.SearchIndex, indexes.Indexable):
    name = indexes.CharField(model_attr='name')
    categories = indexes.MultiValueField(indexed=True, stored=True)
    text = VariationCharField(document=True, use_template=True)
    network_location = SearchableBooleanField(model_attr='is_external')

    def get_model(self):
        return Link

    def prepare_categories(self, link):
        return [categories.name for categories in link.categories.all()]
