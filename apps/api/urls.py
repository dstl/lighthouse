# (c) Crown Owned Copyright, 2016. Dstl.

from django.conf.urls import patterns, url

from .views import LinkUsageAPI

urlpatterns = patterns(
    '',
    url(
        r'^links/(?P<pk>\d+)/usage',
        LinkUsageAPI.as_view(),
        name='api-link-usage',
    ),
)
