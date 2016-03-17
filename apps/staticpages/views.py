# (c) Crown Owned Copyright, 2016. Dstl.
# apps/staticpages/views.py
from django.views.generic.base import TemplateView
from django.conf import settings
import markdown
import codecs
import os


class StaticPageView(TemplateView):
    template_name = 'staticpages/static.html'

    def get_context_data(self, **kwargs):
        context = super(StaticPageView, self).get_context_data(**kwargs)
        slug = kwargs['slug']
        file = os.path.join(
            settings.BASE_DIR,
            'apps',
            'staticpages',
            'pages',
            '%s.md' % slug
        )
        input_file = codecs.open(
            file,
            mode="r",
            encoding="utf-8"
        )
        text = input_file.read()
        html = markdown.markdown(text)
        context['html_content'] = html
        return context
