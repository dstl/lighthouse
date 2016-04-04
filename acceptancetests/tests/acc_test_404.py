# (c) Crown Owned Copyright, 2016. Dstl.

import os
import unittest

from splinter import Browser


class Test404Page (unittest.TestCase):
    def setUp(self):
        self.browser = Browser('phantomjs')

    def test_404_page_appears(self):
        url = "http://%s/nonsense-doesnt-exist" % os.environ['LIGHTHOUSE_HOST']
        title = '404 Not Found'

        self.browser.visit(url)

        self.assertEqual(self.browser.url, url)
        self.assertEqual(self.browser.status_code.code, 404)
        self.assertIn(title, self.browser.title)

        self.assertIn('404 Not Found', self.browser.html)
        # Make sure there's a link to the homepage
        self.assertIn('<a href="/">Lighthouse homepage</a>', self.browser.html)
