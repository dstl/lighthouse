from django.views.generic.base import TemplateView
from apps.users.models import User


class LoginView(TemplateView):
    template_name = 'login.html'

    def get_context_data(self, **kwargs):
        context = super(LoginView, self).get_context_data(**kwargs)
        context['users'] = User.objects.all()
        return context
