# (c) Crown Owned Copyright, 2016. Dstl.

from django.conf.urls import patterns, url


urlpatterns = patterns(
    '',
    url(r'^', 'apps.search.views.search', name="search"),
)
