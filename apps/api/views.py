# (c) Crown Owned Copyright, 2016. Dstl.

import os

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View, RedirectView
from django.views.generic.detail import SingleObjectMixin

from apps.links.models import Link
from apps.staticpages.views import StaticPageViewBase


class APIBase(View):
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super(APIBase, self).dispatch(request, *args, **kwargs)


class APIDocView(StaticPageViewBase):
    template_name = 'api/documentation.html'

    def get_markdown_directory(self):
        return os.path.join(
            settings.BASE_DIR,
            'apps',
            'api',
            'documentation',
        )


class APIHome(APIDocView):
    slug = 'index'


class APIDocHomeRedirect(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        # implemented as method not as `url` instance
        # variable to avoid circular import problem
        return reverse('api-home')


class LinkUsageAPI(SingleObjectMixin, APIBase):
    model = Link

    # TODO (probably)
    # - there is no authentication
    # - there is no way to discover link IDs
    # - there is no way to discover user slugs

    def get(self, request, *args, **kwargs):
        """ Return the usage stats as JSON """
        link = self.get_object()
        response = []
        for use in link.usage.all():
            response.append({
                'user': use.user.userid,
                'date': use.start,
                'duration': use.duration,
            })
        return JsonResponse(response, safe=False)

    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        """ Add new usage stat """

        link = self.get_object()

        # user param is required
        if 'user' not in request.POST:
            return JsonResponse({'error': 'user required'}, status=400)

        # user must exist
        try:
            user = get_user_model().objects.get(slug=request.POST.get('user'))
        except get_user_model().DoesNotExist:
            return JsonResponse({'error': 'no such user'}, status=400)

        link.register_usage(user)
        return JsonResponse({'status': 'ok'}, status=201)
