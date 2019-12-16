# This file exists only to allow python setup.py test to work.

import os
import sys

from django.conf import settings
from django.test.utils import get_runner

os.environ["DJANGO_SETTINGS_MODULE"] = "survey.settings"
test_dir = os.path.dirname(__file__)
sys.path.insert(0, test_dir)


def runtests():
    test_runner = get_runner(settings)
    failures = test_runner([], verbosity=1, interactive=True)
    sys.exit(failures)


if __name__ == "__main__":
    runtests()
