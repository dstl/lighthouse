# (c) Crown Owned Copyright, 2016. Dstl.

from django.core.urlresolvers import reverse
from django.shortcuts import redirect
from django.views.generic.base import View


class Home(View):

    #   Get the homepage. If the user isn't logged in, (we can find no trace
    #   of the user) or they are logged in but somehow don't have a valid slug
    #   then we bounce them to the login page.
    #   Otherwise (for the moment) we take them to the list of links.
    def get(self, request, *args, **kwargs):
        try:
            u = request.user.slug
            if (u is not None and u is not ''):
                return redirect(reverse('link-list'))
            else:
                return redirect(reverse('login'))
        except:
            return redirect(reverse('login'))
