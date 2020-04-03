# -*- coding: utf-8 -*-

from survey.tests.models import BaseModelTest


class TestResponse(BaseModelTest):
    def test_unicode(self):
        """ Unicode generation. """
        self.assertIsNotNone(str(self.response))
