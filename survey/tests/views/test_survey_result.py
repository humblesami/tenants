# -*- coding: utf-8 -*-

from django.urls.base import reverse

from survey.tests.management.test_management import TestManagement


class TestSurveyResult(TestManagement):
    def test_survey_result(self):
        """ We need logging for survey result if the survey need login. """
        url = reverse("survey-result", args=(2,))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("survey-result", args=(1,)))
        self.assertEqual(response.status_code, 302)
        self.login()
        response = self.client.get(reverse("survey-result", args=(2,)))
        self.assertEqual(response.status_code, 200)
        response = self.client.get(reverse("survey-result", args=(1,)))
        self.assertEqual(response.status_code, 200)
