from splinter import Browser
import unittest
import os


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
        self.assertIn(self.browser.title, title)

        self.assertIn('Hello Login', self.browser.html)
