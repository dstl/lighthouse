# (c) Crown Owned Copyright, 2016. Dstl.

from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.views.generic.base import View


class Home(View):

    #   Get the homepage. If we find the keycloak username header,
    #   then log them in and direct to the list of tools. If not, then
    #   check for the slug and either send them to the list of tools
    #   or bounce them to login.
    def get(self, request, *args, **kwargs):
        try:
            u = request.user.slug
            if (u is not None and u is not ''):
                return redirect(reverse('link-list'))
            else:
                return redirect(reverse('login'))
        except:
            return redirect(reverse('login'))
