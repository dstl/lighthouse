# (c) Crown Owned Copyright, 2016. Dstl.
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.views.generic.base import TemplateView, View
from apps.users.models import User
from django.contrib.auth import authenticate, login, logout


class LoginView(TemplateView):
    template_name = 'login.html'

    def get_context_data(self, **kwargs):
        context = super(LoginView, self).get_context_data(**kwargs)
        context['users'] = User.objects.all()
        if 'next' in self.request.GET:
            context['next'] = self.request.GET.get('next')
        return context


class LoginUser(View):

    def get(self, request, *args, **kwargs):
        user = authenticate(slug=kwargs['slug'])
        if user is not None:
            login(request, user)

            #   Check to see if we are missing extra information such as
            #   username, in which case bounce them to the update-profile
            #   page.
            #   NOTE: We can't stop the user from moving away from this
            #   page, so it's totally possible to have a user running around
            #   the place with no username and only a 'stub'.
            #   As somepoint we'll *always* bounce the user to here if
            #   they don't have a username.
            """
            if (user.username is None or
                    user.username is ''):
                return redirect(
                    reverse(
                        'user-updateprofile',
                        kwargs={'slug': user.slug}
                    )
                )
            else:
                return redirect(reverse('link-list'))
            """
            if 'next' in request.GET:
                return redirect(self.request.GET.get('next'))

            return redirect(reverse('link-list'))
        else:
            return redirect(reverse('login-view'))


class Logout(View):

    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect(reverse('login-view'))
