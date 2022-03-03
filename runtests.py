#!/usr/bin/env python
import os
from shutil import rmtree
import sys
import django
from django.conf import settings
from django.test.utils import get_runner


if __name__ == "__main__":
    os.environ['DJANGO_SETTINGS_MODULE'] = 'tests.busker_test_settings'
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["tests"])
    rmtree(settings.MEDIA_ROOT)
    sys.exit(bool(failures))
