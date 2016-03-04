# (c) Crown Owned Copyright, 2016. Dstl.
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.core.urlresolvers import reverse
from django.views.generic.base import TemplateView, View
from apps.users.models import User
from django.contrib.auth import authenticate, login, logout


#   This is the function that actually logs a user in, if they exists then
#   we just create them. If they don't then we create them, authenticate
#   and log them in.
#   TODO: There's a fair amount of refactoring we can do around this, but
#   that's probably best left for when we do LDAP stuff
def LogUserIn(self, request, slug):

    #   See if we an authenticate the user
    try:
        user = authenticate(slug=slug)
    except:
        user = None

    #   If we can, then we log them in, then workout where the heck
    #   to send them.
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
        if (user.username is None or
                user.username is ''):
            return reverse(
                    'user-updateprofile',
                    kwargs={'slug': user.slug}
                )

        if 'next' in request.GET:
            return self.request.GET.get('next')

        return reverse(
                'user-detail',
                kwargs={'slug': user.slug}
            )

    else:

        #   We need to create the user, log them in and redirect them to
        #   give us more information (because they obviously wont have
        #   any yet)
        new_user = User(slug=slug)
        new_user.save()
        user = authenticate(slug=slug)
        login(request, user)
        return reverse(
                'user-updateprofile',
                kwargs={'slug': user.slug}
            )


#   This handles the login form, if nothing is posted then we are just
#   displaying the template. If we have POST data then we are attempting
#   to either create a new user, or log an existing user in.
class LoginRequest(TemplateView):
    template_name = 'login.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['users'] = User.objects.all()
        if 'next' in self.request.GET:
            context['next'] = self.request.GET.get('next')
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        return HttpResponseRedirect(
            LogUserIn(
                self,
                request,
                request.POST.get('slug')
            )
        )


class LoginUser(View):

    def get(self, request, *args, **kwargs):
        return LogUserIn(self, request, kwargs['slug'])


class Logout(View):

    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect(reverse('login-view'))
