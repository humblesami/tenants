# -*- coding: utf-8 -*-

from survey.exporter.tex.question2tex_sankey import Question2TexSankey
from survey.tests.management.test_management import TestManagement


class TestQuestion2TexSankey(TestManagement):
    def test_other_question_type(self):
        """ We get a type error if we do not give a Question. """
        question = self.survey.questions.get(text="Aèbc?")
        q2s = Question2TexSankey(question)
        other_question = self.survey.questions.get(text="Aèbc?")
        self.assertRaises(TypeError, q2s.tex, "other_question")
        self.assertIsNotNone(q2s.tex(other_question))


# Creating a big ranking survey with user takes a long time
"""
    def test_big_ranking_survey(self):
        """ """
        self.create_big_ranking_survey(with_user=True)
        qtext = "How much do you like question {} ?"
        q4 = Question.objects.get(text=qtext.format(4))
        q5 = Question.objects.get(text=qtext.format(5))
        q2tex_sankey = Question2TexSankey(q4, filter=["1"],
                                          group_together={"A" : ["2", "3"]})
        q2tex_sankey.tex(q5)
"""
