# (c) Crown Owned Copyright, 2016. Dstl.

from apps.users.models import User


class SuperBasicAuth(object):

    def get_user(self, slug=None):

        #   Try and get the user by slug, if that doesn't work then
        #   fetch by id
        user = None
        try:
            user = User.objects.get(slug=slug)
        except User.DoesNotExist:
            try:
                user = User.objects.get(pk=slug)
            except User.DoesNotExist:
                return None

        return user

    def authenticate(self, slug=None):
        return self.get_user(slug)
