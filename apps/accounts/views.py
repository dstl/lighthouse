# (c) Crown Owned Copyright, 2016. Dstl.

from django.contrib.auth import REDIRECT_FIELD_NAME, login, logout
from django.core.exceptions import NON_FIELD_ERRORS 
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.generic.edit import FormView

from .forms import AuthenticationForm


class LoginView(FormView):
    form_class = AuthenticationForm
    redirect_field_name = REDIRECT_FIELD_NAME
    template_name = 'accounts/login.html'

    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, *args, **kwargs):
        return super(LoginView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        """
        The user has provided valid credentials (this was checked in
        AuthenticationForm.is_valid()). So now we can check the test cookie
        stuff and log them in.
        """
        self.check_and_delete_test_cookie()
        login(self.request, form.get_user())
        return super(LoginView, self).form_valid(form)

    def form_invalid(self, form):
        """
        The user has provided invalid credentials (this was checked in
        AuthenticationForm.is_valid()). So now we set the test cookie again
        and re-render the form with errors.
        """
        self.set_test_cookie()
        if form.has_error(NON_FIELD_ERRORS, 'admin_user'):
            return HttpResponseRedirect('/admin/')
        return super(LoginView, self).form_invalid(form)

    def get_success_url(self):
        return reverse('user-updateprofile', kwargs={'slug': self.request.user.slug})

    def set_test_cookie(self):
        self.request.session.set_test_cookie()

    def check_and_delete_test_cookie(self):
        if self.request.session.test_cookie_worked():
            self.request.session.delete_test_cookie()
            return True
        return False

    def get(self, request, *args, **kwargs):
        self.set_test_cookie()
        return super(LoginView, self).get(request, *args, **kwargs)


class LogoutView(TemplateView):
    template_name = 'accounts/logout.html'

    def get_next_url(self):
        next = self.request.POST.get('next', None)
        if next is None:
            next = reverse('home')
        return next

    def get(self, request):
        if not request.user.is_authenticated():
            return HttpResponseRedirect(self.get_next_url())
        return super(LogoutView, self).get(request)

    def post(self, request):
        logout(request)
        return HttpResponseRedirect(self.get_next_url())
