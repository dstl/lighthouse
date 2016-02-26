# apps/users/views.py
from django.views.generic import CreateView, DetailView, ListView

from .models import User


class UserDetail(DetailView):
    model = User


class UserCreate(CreateView):
    model = User
    fields = ['fullName', 'phone', 'email']


class UserList(ListView):
    model = User
    paginate_by = 5
