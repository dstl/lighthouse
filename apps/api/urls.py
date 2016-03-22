# (c) Crown Owned Copyright, 2016. Dstl.

from django.conf.urls import patterns, url

from .views import APIHome, APIDocView, LinkUsageAPI, APIDocHomeRedirect

urlpatterns = patterns(
    '',
    url(
        r'^$',
        APIHome.as_view(),
        name='api-home',
    ),
    url(
        r'^docs/$',
        APIDocHomeRedirect.as_view(),
    ),
    url(
        r'^docs/(?P<slug>[\w-]+)$',
        APIDocView.as_view(),
        name='api-doc',
    ),
    url(
        r'^links/(?P<pk>\d+)/usage',
        LinkUsageAPI.as_view(),
        name='api-link-usage',
    ),
)
