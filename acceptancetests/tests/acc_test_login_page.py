# (c) Crown Owned Copyright, 2016. Dstl.

import os
import unittest

from splinter import Browser


class TestLoginPage (unittest.TestCase):
    def setUp(self):
        self.browser = Browser('phantomjs')

    def test_login_page_appears(self):
        # This needs to come from an environment variable at some point
        # For now, this will only pass if the lighthouse-app-server host is
        # running.
        url = "http://%s/login" % os.environ['LIGHTHOUSE_HOST']
        title = 'Lighthouse'

        self.browser.visit(url)

        self.assertEqual(self.browser.url, url)
        self.assertEqual(self.browser.status_code.code, 200)
        self.assertIn(title, self.browser.title)

        self.assertIn('Login with ID.', self.browser.html)
