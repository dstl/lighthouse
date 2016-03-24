# (c) Crown Owned Copyright, 2016. Dstl.

import codecs
import os

from django.conf import settings
from django.http import Http404
from django.views.generic.base import TemplateView

import markdown


class StaticPageViewBase(TemplateView):
    slug = None

    def get_markdown_directory(self):
        return os.path.join(
            settings.BASE_DIR,
            'apps',
            'staticpages',
            'pages',
        )

    def get_markdown_filename(self):
        return os.path.join(
            self.get_markdown_directory(),
            '%s.md' % self.slug
        )

    def get_context_data(self, **kwargs):
        context = super(StaticPageViewBase, self).get_context_data(**kwargs)
        if not self.slug:
            self.slug = kwargs['slug']
        filename = self.get_markdown_filename()
        try:
            input_file = codecs.open(
                filename,
                mode="r",
                encoding="utf-8"
            )
        except FileNotFoundError:
            raise Http404
        text = input_file.read()
        html = markdown.markdown(text)
        context['html_content'] = html
        return context


class StaticPageView(StaticPageViewBase):
    template_name = 'staticpages/static.html'
