# (c) Crown Owned Copyright, 2016. Dstl.

from django.contrib.auth import REDIRECT_FIELD_NAME, login, logout
from django.core.exceptions import NON_FIELD_ERRORS
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.generic import (
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
    View,
)
from django.views.generic.edit import FormView

from haystack.inputs import AutoQuery
from haystack.query import SearchQuerySet

from .forms import AuthenticationForm
from .models import User
from apps.access import LoginRequiredMixin
from apps.organisations.models import Organisation
from apps.teams.models import Team
from apps.links.models import Link


class LoginView(FormView):
    form_class = AuthenticationForm
    redirect_field_name = REDIRECT_FIELD_NAME
    template_name = 'accounts/login.html'
    user = None

    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super(LoginView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        """
        The user has provided valid credentials (this was checked in
        AuthenticationForm.is_valid()). So now we can check the test cookie
        stuff and log them in.
        """
        self.check_and_delete_test_cookie()
        self.user = form.get_user()
        login(self.request, self.user)
        return super(LoginView, self).form_valid(form)

    def form_invalid(self, form):
        """
        The user has provided invalid credentials (this was checked in
        AuthenticationForm.is_valid()). So now we set the test cookie again
        and re-render the form with errors.
        """
        self.set_test_cookie()
        if form.has_error(NON_FIELD_ERRORS, 'admin_user'):
            return HttpResponseRedirect('/admin/')
        return super(LoginView, self).form_invalid(form)

    def get_success_url(self):
        # Explicit "next" page overrides prompts for more user info
        if 'next' in self.request.GET:
            return self.request.GET.get('next')

        # If they don't have a name set
        if not self.user.name:
            return reverse(
                'user-updateprofile',
                kwargs={'slug': self.user.slug}
            )

        # If they don't have a team set
        if self.user.teams.count() == 0:
            return reverse(
                'user-update-teams',
                kwargs={'slug': self.user.slug}
            )

        # If they have a name and a team, but are missing extra information
        if (not self.user.best_way_to_find or
                not self.user.best_way_to_contact or
                not self.user.phone or
                not self.user.email):
            return reverse(
                'user-updateprofile',
                kwargs={'slug': self.user.slug}
            )

        return reverse('user-detail', kwargs={'slug': self.user.slug})

    def set_test_cookie(self):
        self.request.session.set_test_cookie()

    def check_and_delete_test_cookie(self):
        if self.request.session.test_cookie_worked():
            self.request.session.delete_test_cookie()
            return True
        return False

    def get(self, request, *args, **kwargs):
        """
        Same as django.views.generic.edit.ProcessFormView.get(),
        but adds test cookie stuff
        """
        self.set_test_cookie()
        return super(LoginView, self).get(request, *args, **kwargs)


class LogoutView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/logout.html'

    def get_next_url(self):
        next = self.request.POST.get('next', None)
        if next is None:
            next = reverse('home')
        return next

    def get(self, request):
        if not request.user.is_authenticated():
            return HttpResponseRedirect(self.get_next_url())
        return super(LogoutView, self).get(request)

    def post(self, request):
        logout(request)
        return HttpResponseRedirect(self.get_next_url())


class UserDetail(LoginRequiredMixin, DetailView):
    model = User


class UserUpdateProfileTeams(LoginRequiredMixin, UpdateView):
    model = User
    fields = [
                'name',
                'best_way_to_find',
                'best_way_to_contact',
                'phone',
                'email'
            ]
    template_name = 'users/user_details_teams_form.html'

    def get_context_data(self, **kwargs):
        context = super(
            UserUpdateProfileTeams,
            self
        ).get_context_data(**kwargs)

        #   We want to grab all the teams so we can display a bunch of
        #   checkboxes allowing the user to join those teams
        if self.request.user.is_authenticated():
            teams = Team.objects.all()
            for team in teams:
                team.checked = False
                for us in self.request.user.teams.all():
                    if team.id == us.id:
                        team.checked = True

            context['teams'] = teams

        context['organisations'] = Organisation.objects.all()

        return context


class UserUpdateProfile(LoginRequiredMixin, UpdateView):
    model = User
    fields = [
                'name',
                'best_way_to_find',
                'best_way_to_contact',
                'phone',
                'email'
            ]
    template_name = 'users/user_details_form.html'

    # Only show this form if it's for the currently logged in user.
    def get(self, request, *args, **kwargs):
        if (self.request.user.slug != kwargs['slug']):
            return HttpResponseRedirect(
                reverse('user-detail', kwargs={'slug': kwargs['slug']})
            )
        return super(UserUpdateProfile, self).get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(UserUpdateProfile, self).get_context_data(**kwargs)
        if (
            self.request.user.name is None or
            self.request.user.name == ''
        ):
            context['show_name_alert'] = True
        else:
            if (
                self.request.user.best_way_to_find is None or
                self.request.user.best_way_to_find == '' or
                self.request.user.best_way_to_contact is None or
                self.request.user.best_way_to_contact == '' or
                self.request.user.phone is None or
                self.request.user.phone == '' or
                self.request.user.email is None or
                self.request.user.email == ''
            ):
                context['show_extra_details_alert'] = True

        #   We want to grab all the teams so we can display a bunch of
        #   checkboxes allowing the user to join those teams
        if self.request.user.is_authenticated():
            teams = Team.objects.all()
            for team in teams:
                team.checked = False
                for us in self.request.user.teams.all():
                    if team.id == us.id:
                        team.checked = True

            context['teams'] = teams

        context['organisations'] = Organisation.objects.all()

        #   Work out which field we want to focus the user on, by starting
        #   with the least significant first and working up.
        context['highlight_field'] = 'id_name'
        if (self.request.user.email is None or self.request.user.email == ''):
            context['highlight_field'] = 'id_email'
        if (self.request.user.phone is None or self.request.user.phone == ''):
            context['highlight_field'] = 'id_phone'
        if (self.request.user.best_way_to_contact is None or
                self.request.user.best_way_to_contact == ''):
            context['highlight_field'] = 'id_best_way_to_contact'
        if (self.request.user.best_way_to_find is None or
                self.request.user.best_way_to_find == ''):
            context['highlight_field'] = 'id_best_way_to_find'
        if (self.request.user.name is None or
                self.request.user.name == ''):
            context['highlight_field'] = 'id_name'

        #
        return context

    #   Once we've updated the details, go to user profile page
    def get_success_url(self):
        return reverse('user-detail', kwargs={'slug': self.request.user.slug})

    #   Only save the data if the user details match who we currently are
    #   TODO: Don't even show this page if the user slug doesn't match
    def form_valid(self, form):
        userDetails = form.save(commit=False)

        #   Don't do any of this is the user isn't currently logged in
        #   or different to the currently logged in user
        if (self.request.user.is_authenticated() is False or
                userDetails.id != self.request.user.id):
            return HttpResponseRedirect(self.get_success_url())

        #   If we have been passed a name then we have come from the
        #   user details form, if we don't have a name, then we are dealing
        #   with teams.
        if form.data.get('name') is not None:
            userDetails.save()
        else:
            user = User.objects.get(pk=userDetails.pk)
            #   Now we need to dump all the current links to teams and
            #   then add them all back in.
            user.teams.clear()
            for team in form.data.getlist('team'):
                user.teams.add(int(team))

            #   We need to see if we have been passed over a new team name
            #   if so then we have a bunch of work to do around adding that
            #   team
            team_name = form.data.get('teamname')
            if (team_name is not None and team_name is not ''):
                new_organisation_name = form.data.get('new_organisation')
                organisation_id = form.data.get('organisation')

                #   Now check to see if this team is using an existing
                #   organisation or a new_organisation.
                #   If it a new organisation then we need to create it.
                if (new_organisation_name is not None and
                        new_organisation_name is not ''):
                    check_org = Organisation.objects.filter(
                        name=new_organisation_name
                    ).exists()
                    if check_org is True:
                        new_organisation = Organisation.objects.get(
                            name=new_organisation_name
                        )
                    else:
                        new_organisation = Organisation()
                        new_organisation.name = new_organisation_name
                        new_organisation.save()
                else:
                    #   Otherwise we are going to use the organisation we
                    #   have been passed over.
                    check_org = Organisation.objects.filter(
                        pk=organisation_id).exists()
                    if check_org is True:
                        new_organisation = Organisation.objects.get(
                            pk=organisation_id
                        )
                    else:
                        # TODO: Raise an error here to display on the form
                        return self.render_to_response(self.get_context_data())

                #   Either way we now have a new_organisation object that we
                #   can use to create the team.
                check_team = Team.objects.filter(name=team_name).exists()

                if check_team is True:
                    new_team = Team.objects.filter(name=team_name)
                else:
                    new_team = Team(
                        name=team_name,
                        organisation=new_organisation
                    )
                    new_team.save()

                #   Now add the new team to the teams join on the user
                user.teams.add(new_team.pk)
                user.save()

        #   If the user wants to add another team, do that here
        #   TODO: add a #team thingy to the URL so we can jump down to the
        #   teams section
        submit_action = form.data.get('submit_action')
        if (submit_action is not None and submit_action is not ''):
            if submit_action in ['Save and add a new team',
                                 'Save and manage team membership']:
                return HttpResponseRedirect(
                    reverse(
                        'user-update-teams',
                        kwargs={
                            'slug': self.request.user.slug
                        }
                    )
                )

        #   Normally we'd just go back to their profile page. So we'll do
        #   that here.
        return HttpResponseRedirect(self.get_success_url())


class UserList(LoginRequiredMixin, ListView):
    model = User
    paginate_by = 50
    template_name = 'users/user_list.html'

    def get_context_data(self, **kwargs):
        context = super(UserList, self).get_context_data(**kwargs)

        context['top_teams'] = Team.with_most_members()
        context['top_organisations'] = Organisation.with_most_teams()
        context['total_users_in_db'] = User.objects.count()

        if self.has_query():
            context['query'] = self.request.GET['q']
            context['results_length'] = len(context['object_list'])

        return context

    def has_query(self):
        return 'q' in self.request.GET and len(self.request.GET['q']) > 0

    def get_queryset(self):
        if self.has_query():
            queryset = SearchQuerySet().filter(
                content=AutoQuery(self.request.GET['q']),
            ).models(User)
        else:
            queryset = super(UserList, self).get_queryset()

        return queryset


class UserFavouritesAdd(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        link_id = request.POST.get('link_id')
        link = Link.objects.get(pk=link_id)
        link_url = reverse('link-detail', kwargs={'pk': link_id})
        request.user.favourites.add(link)
        return HttpResponseRedirect(link_url)


class UserFavouritesRemove(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        link_id = request.POST.get('link_id')
        link = Link.objects.get(pk=link_id)
        link_url = reverse('link-detail', kwargs={'pk': link_id})
        request.user.favourites.remove(link)
        return HttpResponseRedirect(link_url)
