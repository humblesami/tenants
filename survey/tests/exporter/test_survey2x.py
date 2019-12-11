# -*- coding: utf-8 -*-

import logging
import os
from datetime import datetime

import pytz
from django.conf import settings
from mock.mock import patch

from survey.exporter.survey2x import Survey2X
from survey.tests.management.test_management import TestManagement

LOGGER = logging.getLogger(__name__)


class Survey2Survey(Survey2X):
    def survey_to_x(self):
        pass


LONG_TIME_AGO = datetime(1990, 1, 1, 0, 0, 0)
SHORT_TIME_AGO = datetime(2000, 1, 1, 0, 0, 0)
RIGHT_NOW = datetime(2010, 1, 1, 0, 0, 0)


class TestSurvey2X(TestManagement):
    def setUp(self):
        TestManagement.setUp(self)
        self.virtual_survey2x = Survey2X(self.survey)
        self.actual_survey2x = Survey2Survey(self.survey)
        self.expected_actual = os.path.join(
            settings.ROOT, "survey", "test-management-survey.survey"
        )
        self.expected_virtual = os.path.join(
            settings.ROOT, "x", "test-management-survey.x"
        )

    def get_fail_info(self, survey2x):
        msg = "\nLatest answer date :     {}".format(survey2x.latest_answer_date)
        msg += "\nFile modification time : {}".format(survey2x.file_modification_time)
        return msg

    def test_survey_2_x(self):
        self.assertRaises(NotImplementedError, self.virtual_survey2x.survey_to_x)

    def test_file_name(self):
        self.assertEqual(self.actual_survey2x.file_name(), self.expected_actual)
        self.assertEqual(self.virtual_survey2x.file_name(), self.expected_virtual)

    def test_initially_need_update(self):
        self.assertTrue(
            self.actual_survey2x.need_update(),
            "No file exported and the survey "
            "contain response : we should need an update. "
            "{}".format(self.get_fail_info(self.actual_survey2x)),
        )

    @patch.object(Survey2Survey, "file_modification_time", RIGHT_NOW)
    @patch.object(Survey2Survey, "latest_answer_date", LONG_TIME_AGO)
    def test_need_update_after_generation(self):
        self.assertFalse(
            self.actual_survey2x.need_update(),
            "We exported the file and there"
            " is no new response, we should not need an update. "
            "{}".format(self.get_fail_info(self.actual_survey2x)),
        )

    @patch.object(Survey2Survey, "file_modification_time", LONG_TIME_AGO)
    @patch.object(Survey2Survey, "latest_answer_date", RIGHT_NOW)
    def test_need_update_after_new_response(self):
        self.assertTrue(
            self.actual_survey2x.need_update(),
            "We exported the file but there"
            " is a new response, we should need an update. "
            "{}".format(self.get_fail_info(self.actual_survey2x)),
        )
