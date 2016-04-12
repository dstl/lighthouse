# (c) Crown Owned Copyright, 2016. Dstl.

from apps.links.models import Link


class MetaUsageMiddleware(object):
    def process_request(self, request):
        if request.user.is_authenticated():
            lighthouse = Link.objects.get(id=1)
            lighthouse.register_usage(request.user)

        return None
