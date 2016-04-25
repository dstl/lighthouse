# (c) Crown Owned Copyright, 2016. Dstl.
# TODO
# This is borrowed from django 1.9 and can be removed when either:
# - haystack supports django 1.9
# - haystack is no longer a dependency

from os import getenv

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import ImproperlyConfigured, PermissionDenied
from django.utils.encoding import force_text


class LoginUsingEnvironmentMixin(object):
    """
    Verify that the current logged-in user matches the user passed
    in the environment.
    """
    def dispatch(self, request, *args, **kwargs):
        user = getenv('REMOTE_USER')
        if user and user != request.user.userid:
            return self.handle_no_permission()
        return super(LoginUsingEnvironmentMixin, self).dispatch(
            request, *args, **kwargs)


class AccessMixin(object):
    """
    Abstract CBV mixin that gives access mixins the same customizable
    functionality.
    """
    login_url = None
    permission_denied_message = ''
    raise_exception = False
    redirect_field_name = REDIRECT_FIELD_NAME

    def get_login_url(self):
        """
        Override this method to override the login_url attribute.
        """
        login_url = self.login_url or settings.LOGIN_URL
        if not login_url:
            raise ImproperlyConfigured(
                '{0} is missing the login_url attribute.'
                ' Define {0}.login_url, settings.LOGIN_URL, or override '
                '{0}.get_login_url().'.format(self.__class__.__name__)
            )
        return force_text(login_url)

    def get_permission_denied_message(self):
        """
        Override this method to override the permission_denied_message
        attribute.
        """
        return self.permission_denied_message

    def get_redirect_field_name(self):
        """
        Override this method to override the redirect_field_name attribute.
        """
        return self.redirect_field_name

    def handle_no_permission(self):
        if self.raise_exception:
            raise PermissionDenied(self.get_permission_denied_message())
        return redirect_to_login(
            self.request.get_full_path(),
            self.get_login_url(),
            self.get_redirect_field_name()
        )


class LoginRequiredMixin(LoginUsingEnvironmentMixin, AccessMixin):
    """
    CBV mixin which verifies that the current user is authenticated.
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated():
            return self.handle_no_permission()
        return super(LoginRequiredMixin, self).dispatch(
            request, *args, **kwargs)
