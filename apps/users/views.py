from django.views.generic import CreateView, DetailView, ListView, TemplateView

from .models import User


class UserDetail(DetailView):
    model = User


class UserCreate(CreateView):
    model = User
    fields = ['fullName', 'phone', 'email']


class UserList(ListView):
    model = User
    paginate_by = 5


class WhoAmI(TemplateView):
    template_name = 'user_page.html'

    def get_context_data(self, **kwargs):
        context = super(WhoAmI, self).get_context_data(**kwargs)
        return context
