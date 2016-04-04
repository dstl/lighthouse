# (c) Crown Owned Copyright, 2016. Dstl.
"""lighthouse URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url
from django.contrib import admin

from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from apps.links.views import (
    LinkCreate,
    LinkDetail,
    LinkInterstitial,
    LinkList,
    LinkStats,
    LinkStatsCSV,
    LinkUpdate,
    LinkRedirect,
    OverallLinkStats,
    OverallLinkStatsCSV,
)

from apps.users.views import (
    UserDetail,
    UserUpdateProfile,
    UserUpdateProfileTeams,
    UserList,
)

from apps.organisations.views import (
    OrganisationCreate,
    OrganisationDetail,
    OrganisationList,
)

from apps.teams.views import (
    TeamCreate,
    TeamDetail,
    TeamList,
    TeamJoin,
    TeamLeave,
)
from apps.home.views import Home
from apps.staticpages.views import StaticPageView, Status404View, Status500View
from apps.search.views import (
    SearchStats,
    SearchStatsCSV
)
from apps.accounts.views import (
    LoginView,
    LogoutView,
)


handler404 = Status404View.as_view()
handler500 = Status500View.as_view()

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(
        r'^login/$',
        LoginView.as_view(),
        name='login',
    ),
    url(
        r'^logout$',
        LogoutView.as_view(),
        name='logout',
    ),

    url(r'^$', Home.as_view(), name="home"),
    url(
        r'^users/?$',
        UserList.as_view(),
        name='user-list',
    ),
    url(
        r'^users/(?P<slug>[\w-]+)/update-profile/teams/?$',
        UserUpdateProfileTeams.as_view(),
        name='user-update-teams',
    ),
    url(
        r'^users/(?P<slug>[\w-]+)/update-profile/?$',
        UserUpdateProfile.as_view(),
        name='user-updateprofile',
    ),
    url(
        r'^users/(?P<slug>[\w-]+)/?$',
        UserDetail.as_view(),
        name='user-detail',
    ),
    url(
        r'^links/?$',
        LinkList.as_view(),
        name='link-list',
    ),
    url(
        r'^links/(?P<pk>\d+)/?$',
        LinkDetail.as_view(),
        name='link-detail',
    ),
    url(
        r'^links/(?P<pk>\d+)/stats$',
        LinkStats.as_view(),
        name='link-stats',
    ),
    url(
        r'^links/(?P<pk>\d+)/stats.csv$',
        LinkStatsCSV.as_view(),
        name='link-stats-csv',
    ),
    url(
        r'^links/(?P<pk>\d+)/redirect/?$',
        LinkRedirect.as_view(),
        name='link-redirect',
    ),
    url(
        r'^links/(?P<pk>\d+)/go/?$',
        LinkInterstitial.as_view(),
        name='link-interstitial',
    ),
    url(
        r'^links/(?P<pk>\d+)/edit/?$',
        LinkUpdate.as_view(),
        name='link-edit',
    ),
    url(
        r'^links/new/?$',
        LinkCreate.as_view(),
        name='link-create',
    ),
    url(
        r'^links/stats$',
        OverallLinkStats.as_view(),
        name='link-overall-stats',
    ),
    url(
        r'^links/stats.csv$',
        OverallLinkStatsCSV.as_view(),
        name='link-overall-stats-csv',
    ),
    url(
        r'^organisations/?$',
        OrganisationList.as_view(),
        name='organisation-list',
    ),
    url(
        r'^organisations/new/?$',
        OrganisationCreate.as_view(),
        name='organisation-create',
    ),
    url(
        r'^organisations/(?P<pk>\d+)/?$',
        OrganisationDetail.as_view(),
        name='organisation-detail',
    ),
    url(
        r'^organisations/(?P<org_id>\d+)/teams/new/?$',
        TeamCreate.as_view(),
        name='organisation-team-create',
    ),
    url(
        r'^teams/?$',
        TeamList.as_view(),
        name='team-list',
    ),
    url(
        r'^teams/new/?$',
        TeamCreate.as_view(),
        name='team-create',
    ),
    url(
        r'^teams/(?P<pk>\d+)/join/?$', TeamJoin.as_view(), name='team-join', ),
    url(
        r'^teams/(?P<pk>\d+)/leave/?$',
        TeamLeave.as_view(),
        name='team-leave', ),
    url(
        r'^teams/(?P<pk>\d+)/?$',
        TeamDetail.as_view(),
        name='team-detail',
    ),

    url(
        r'^api/',
        include('apps.api.urls'),
    ),

    url(
        r'^search/stats/?$',
        SearchStats.as_view(),
        name='search-stats',
    ),

    url(
        r'^search/stats.csv$',
        SearchStatsCSV.as_view(),
        name='search-stats-csv',
    ),

    url(
        r'^(?P<slug>\w+)/?$',
        StaticPageView.as_view(),
        name='static-page'
    ),
]
urlpatterns += staticfiles_urlpatterns()
