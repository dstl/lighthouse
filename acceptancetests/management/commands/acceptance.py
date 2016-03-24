# (c) Crown Owned Copyright, 2016. Dstl.

from os import path
import sys
import unittest

from django.core.management.base import BaseCommand


def thisDir():
    return path.dirname(path.realpath(__file__))


class Command(BaseCommand):
    help = 'Runs all the tests in the acceptancetests directory'

    def handle(self, *args, **options):
        loader = unittest.TestLoader()
        tests = loader.discover(
            './acceptancetests/tests',
            pattern="acc_test_*.py"
        )

        runner = unittest.TextTestRunner(verbosity=2)

        test_result = runner.run(tests)

        if test_result.wasSuccessful():
            sys.exit()
        else:
            number_failed = len(test_result.failures) + len(test_result.errors)
            sys.exit(number_failed)
