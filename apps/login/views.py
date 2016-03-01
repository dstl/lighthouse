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
        return context


class LoginUser(View):

    def get(self, request, *args, **kwargs):
        user = authenticate(user_id=kwargs['pk'])
        if user is not None:
            login(request, user)
            request.session['pet'] = 'fish'
            return redirect(reverse('user-detail', kwargs={'pk': user.pk}))
        else:
            return redirect(reverse('login-view'))


class Logout(View):

    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect(reverse('login-view'))
