# (c) Crown Owned Copyright, 2016. Dstl.

from django.contrib.auth import authenticate, login, logout
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.utils.text import slugify
from django.views.generic.base import TemplateView, View

from apps.users.models import User


#   This is the function that actually logs a user in, if they exists then
#   we just create them. If they don't then we create them, authenticate
#   and log them in.
#   TODO: There's a fair amount of refactoring we can do around this, but
#   that's probably best left for when we do LDAP stuff
def LogUserIn(self, request, slug):
    # pdb.set_trace()
    #   See if we an authenticate the user
    try:
        user = authenticate(slug=slugify(slug))
    except:
        user = None

    #   If we can, then we log them in, then workout where the heck
    #   to send them.
    if user is not None:
        login(request, user)

        if 'next' in request.GET:
            return self.request.GET.get('next')

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

        #   If they don't have a team, bounce them to add one
        if user.teams.count() == 0:
            return reverse(
                    'user-update-teams',
                    kwargs={'slug': user.slug}
                )

        #   If they have a username and teams, yay go them! But, they may
        #   not have added any extra information yet, we should probably
        #   nag them into doing that.
        if (user.best_way_to_find == '' or
                user.best_way_to_contact == '' or
                user.phone == '' or
                user.email == ''):
            return reverse(
                    'user-updateprofile',
                    kwargs={'slug': user.slug}
                )

        return reverse(
                'user-detail',
                kwargs={'slug': user.slug}
            )

    else:

        #   We need to create the user, log them in and redirect them to
        #   give us more information (because they obviously wont have
        #   any yet). But not if it's an empty slug!
        if slug == '' or slug is None:
            return reverse('home')

        #   We could add the act of slugifying onto the user object itself
        #   to make it self cleaning. But at this code is going to be
        #   refactored here anyway, when we start logging the user in via
        #   LDAP (or whatever), I don't want something somewhere else effecting
        #   the values. i.e. we change this code here, but the User object
        #   is still mutating the value.
        #   TODO: Refactor this code for the proper login code.
        new_user = User(slug=slugify(slug), original_slug=slug)
        new_user.save()
        user = authenticate(slug=new_user.slug)
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
