from apps.users.models import User


class SuperBasicAuth(object):

    def get_user(self, user_id=None):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def authenticate(self, user_id=None):
        return self.get_user(user_id)
