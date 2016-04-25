# (c) Crown Owned Copyright, 2016. Dstl.

from haystack import indexes

from .models import User


class UserIndex(indexes.SearchIndex, indexes.Indexable):
    name = indexes.CharField(model_attr='name')
    slug = indexes.CharField(model_attr='slug')
    full_name = indexes.CharField(model_attr='full_name')
    text = indexes.CharField(
        document=True,
        use_template=True)

    def get_model(self):
        return User

    def prepare_categories(self, user):
        return [categories.name for categories in user.categories.all()]
