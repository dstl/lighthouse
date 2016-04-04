# (c) Crown Owned Copyright, 2016. Dstl.

from __future__ import unicode_literals

from django import forms
from django.contrib.auth import get_user_model
from django.utils.text import capfirst
from django.utils.translation import ugettext_lazy as _


class AuthenticationForm(forms.Form):
    userid = forms.CharField(
        max_length=254,
        widget=forms.TextInput(attrs={'autofocus': ''}),
    )

    error_messages = {
        'invalid_login': _("Please enter a correct %(userid)s. "
                           "Note that may be case-sensitive."),
        'inactive': _("This account is inactive."),
        'admin_user': _("Admin users must login via the admin interface.")
    }

    def __init__(self, request=None, *args, **kwargs):
        """
        The 'request' parameter is set for custom auth use by subclasses.
        The form data comes in via the standard 'data' kwarg.
        """
        self.request = request
        self.user_cache = None
        super(AuthenticationForm, self).__init__(*args, **kwargs)

        # Set the label for the "username" field.
        UserModel = get_user_model()
        self.userid_field = UserModel._meta.get_field(UserModel.USERNAME_FIELD)
        if self.fields['userid'].label is None:
            self.fields['userid'].label = capfirst(
                self.userid_field.verbose_name)

    def clean(self):
        userid = self.cleaned_data.get('userid')

        if userid:
            try:
                user = get_user_model().objects.get(userid=userid)
            except:
                user = get_user_model().objects.create_user(
                    userid=userid, is_active=True)

            if user.has_usable_password():
                raise forms.ValidationError(
                    self.error_messages['admin_user'],
                    code='admin_user',
                )
            else:
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                self.user_cache = user

            if self.user_cache is None:
                raise forms.ValidationError(
                    self.error_messages['invalid_login'],
                    code='invalid_login',
                    params={'userid': self.userid_field.verbose_name},
                )
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data

    def confirm_login_allowed(self, user):
        """
        Controls whether the given User may log in. This is a policy
        setting, independent of end-user authentication. This default
        behavior is to allow login by active users, and reject login by
        inactive users. If the given user cannot log in, this method
        should raise a ``forms.ValidationError``. If the given user may
        log in, this method should return None.
        """
        if not user.is_active:
            raise forms.ValidationError(
                self.error_messages['inactive'],
                code='inactive',
            )

    def get_user_id(self):
        if self.user_cache:
            return self.user_cache.id
        return None

    def get_user(self):
        return self.user_cache
