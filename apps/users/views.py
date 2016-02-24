from django.views.generic import CreateView, DetailView, ListView, TemplateView
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from .models import User, Organisation


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


class OrganisationList(ListView):
    model = Organisation


class OrganisationCreate(CreateView):
    model = Organisation
    fields = ['name']

    def post(self, request, *args, **kwargs):
        super(OrganisationCreate, self).post(request, *args, **kwargs)
        return HttpResponseRedirect(reverse('organisation-list'))


class OrganisationDetail(DetailView):
    model = Organisation
