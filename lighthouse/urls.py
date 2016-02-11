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
from apps.links.views import LinkCreate, LinkDetail, LinkList, LinkEdit
from apps.users.views import UserCreate, UserDetail, UserList

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    url(
        r'^users$',
        UserList.as_view(),
        name='user-list',
    ),
    url(
        r'^user/(?P<pk>\d+)$',
        UserDetail.as_view(),
        name='user-detail',
    ),
    url(
        r'^user/new$',
        UserCreate.as_view(),
        name='user-create',
    ),
    url(
        r'^links$',
        LinkList.as_view(),
        name='link-list',
    ),
    url(
        r'^link/(?P<pk>\d+)$',
        LinkDetail.as_view(),
        name='link-detail',
    ),
    url(
        r'^link/(?P<pk>\d+)/edit$',
        LinkEdit.as_view(),
        name='link-edit',
    ),
    url(
        r'^link/new$',
        LinkCreate.as_view(),
        name='link-create',
    ),
]
urlpatterns += staticfiles_urlpatterns()
