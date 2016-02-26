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
        self.browser.visit(url)

        self.assertTrue(self.browser.is_text_present('Hello Login'))
