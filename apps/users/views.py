# (c) Crown Owned Copyright, 2016. Dstl.
# apps/users/views.py
from django.http import HttpResponseRedirect
from django.views.generic import DetailView, ListView, UpdateView
from django.core.urlresolvers import reverse
from .models import User


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

        return context

    #   Once we've updated the details, go back home
    def get_success_url(self):
        return reverse('home')

    #   Only save the data if the user details match who we currently are
    #   TODO: Don't even show this page if the user slug doesn't match
    def form_valid(self, form):
        userDetails = form.save(commit=False)
        if userDetails.id == self.request.user.id:
            userDetails.save()
        return HttpResponseRedirect(self.get_success_url())


class UserList(ListView):
    model = User
