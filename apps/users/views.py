# (c) Crown Owned Copyright, 2016. Dstl.
# apps/users/views.py
from django.http import HttpResponseRedirect
from django.views.generic import DetailView, ListView, UpdateView
from django.core.urlresolvers import reverse
from .models import User
from apps.teams.models import Team
from apps.organisations.models import Organisation


class UserDetail(DetailView):
    model = User


class UserUpdateProfile(UpdateView):
    model = User
    fields = [
                'username',
                'best_way_to_find',
                'best_way_to_contact',
                'phone',
                'email'
            ]
    template_name = 'users/user_details_form.html'

    def get_context_data(self, **kwargs):
        context = super(UserUpdateProfile, self).get_context_data(**kwargs)
        if (
            self.request.user.username is None or
            self.request.user.username == ''
        ):
            context['show_username_alert'] = True
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

        #   Now we need to dump all the current links to teams and
        #   then add them all back in.
        userDetails.teams.clear()
        for team in form.data.getlist('team'):
            userDetails.teams.add(int(team))

        #   We need to see if we have been passed over a new team name
        #   if so then we have a bunch of work to do around adding that team
        team_name = form.data.get('name')
        if (team_name is not None and team_name is not ''):
            new_organisation_name = form.data.get('new_organisation')
            organisation_id = form.data.get('organisation')

            #   Now check to see if this team is using an existing organisation
            #   or a new_organisation.
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
                #   Otherwise we are going to use the organisation we have been
                #   passed over.
                check_org = Organisation.objects.filter(
                    pk=organisation_id).exists()
                if check_org is True:
                    new_organisation = Organisation.objects.get(
                        pk=organisation_id
                    )
                else:
                    # TODO: Raise an error here to display on the form
                    return self.render_to_response(self.get_context_data())

            #   Either way we now have a new_organisation object that we can
            #   use to create the team.
            check_team = Team.objects.filter(name=team_name).exists()

            if check_team is True:
                new_team = Team.objects.filter(name=team_name)
            else:
                new_team = Team(name=team_name, organisation=new_organisation)
                new_team.save()

            #   Now add the new team to the teams join on the user
            userDetails.teams.add(new_team.pk)

        #   Phew, now we save the updated user data.
        userDetails.save()

        #   If the user wants to add another team, do that here
        #   TODO: add a #team thingy to the URL so we can jump down to the
        #   teams section
        submit_action = form.data.get('submit_action')
        if (submit_action is not None and submit_action is not ''):
            if submit_action == 'Save and add a new team':
                return HttpResponseRedirect(
                    reverse(
                        'user-updateprofile',
                        kwargs={
                            'slug': self.request.user.slug
                        }
                    )
                )

        #   Normally we'd just go back to their profile page. So we'll do
        #   that here.
        return HttpResponseRedirect(self.get_success_url())


class UserList(ListView):
    model = User
