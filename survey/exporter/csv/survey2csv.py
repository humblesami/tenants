# -*- coding: utf-8 -*-

import logging

from django.utils.translation import ugettext_lazy as _

from survey.exporter.survey2x import Survey2X

LOGGER = logging.getLogger(__name__)


class Survey2Csv(Survey2X):
    @staticmethod
    def line_list_to_string(line):
        """ Write a line in the CSV. """
        new_line = ""
        for i, cell in enumerate(line):
            cell = " ".join(str(cell).split())
            new_line += cell.replace(",", ";")
            if i != len(line) - 1:
                new_line += ","
        return new_line

    @staticmethod
    def get_user_line(question_order, response):
        """ Creating a line for a user """
        LOGGER.debug("\tTreating answer from %s", response.user)
        user_answers = {}
        try:
            user_answers["user"] = response.user.username
        except AttributeError:
            # 'NoneType' object has no attribute 'username'
            user_answers["user"] = _("Anonymous")
        # user_answers[u"entity"] = response.user.entity
        for answer in response.answers.all():
            answers = answer.values
            cell = ""
            for i, ans in enumerate(answers):
                if i < len(answers) - 1:
                    # Separate by a pipe if its not the last
                    cell += ans + "|"
                else:
                    cell += ans
            LOGGER.debug("\t\t%s : %s", answer.question.pk, cell)
            user_answers[answer.question.pk] = cell
        user_line = []
        for key_ in question_order:
            try:
                user_line.append(user_answers[key_])
            except KeyError:
                user_line.append("")
        return user_line

    def get_header_and_order(self):
        """ Creating header.

        :param Survey survey: The survey we're treating. """
        header = ["user"]  # , u"entity"]
        question_order = ["user"]  # , u"entity" ]
        for question in self.survey.questions.all():
            header.append(question.text)
            question_order.append(question.pk)
        return header, question_order

    def survey_to_x(self):
        csv = []
        header, question_order = self.get_header_and_order()
        csv.append(Survey2Csv.line_list_to_string(header))
        for response in self.survey.responses.all():
            line = Survey2Csv.get_user_line(question_order, response)
            csv.append(Survey2Csv.line_list_to_string(line))
        return "\n".join(csv)
