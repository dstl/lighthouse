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
from django.conf.urls import url
from django.contrib import admin

from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from apps.links.views import (
    LinkCreate,
    LinkDetail,
    LinkList,
    LinkUpdate,
    LinkRedirect,
)

from apps.users.views import (
    UserCreate,
    UserDetail,
    UserUpdateProfile,
    UserList,
)

from apps.organisations.views import (
    OrganisationCreate,
    OrganisationDetail,
    OrganisationList,
)

from apps.teams.views import TeamCreate, TeamDetail, TeamList
from apps.login.views import LoginView, LoginUser, Logout
from apps.home.views import Home

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(r'^login$', LoginView.as_view(), name="login-view"),
    url(
        r'^login/(?P<slug>[\w-]+)$',
        LoginUser.as_view(),
        name="login-user"
    ),
    url(r'^logout$', Logout.as_view(), name="logout"),

    url(r'^$', Home.as_view(), name="home"),
    url(
        r'^users/?$',
        UserList.as_view(),
        name='user-list',
    ),
    url(
        r'^users/new/?$',
        UserCreate.as_view(),
        name='user-create',
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
        r'^links/(?P<pk>\d+)/redirect/?$',
        LinkRedirect.as_view(),
        name='link-redirect',
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
        r'^teams/(?P<pk>\d+)/?$',
        TeamDetail.as_view(),
        name='team-detail',
    ),
]
urlpatterns += staticfiles_urlpatterns()
