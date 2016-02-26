from splinter import Browser
import unittest


class TestLoginPage (unittest.TestCase):
    def setUp(self):
        self.browser = Browser('phantomjs')

    def test_login_page_appears(self):
        # This needs to come from an environment variable at some point
        # For now, this will only pass if the lighthouse-app-server host is
        # running.
        url = "http://10.10.11.10:8080/login"
        self.browser.visit(url)

        self.assertTrue(self.browser.is_text_present('Hello Login'))
