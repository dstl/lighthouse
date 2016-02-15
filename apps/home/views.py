from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.views.generic.base import View


class Home(View):

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return redirect(reverse('whoami'))
        else:
            return redirect(reverse('login-view'))
