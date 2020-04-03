# -*- coding: utf-8 -*-

import logging
import os
from pydoc import locate

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

from survey.exporter.survey2x import Survey2X
from survey.exporter.tex.latex_file import LatexFile
from survey.exporter.tex.question2tex import Question2Tex
from survey.exporter.tex.question2tex_chart import Question2TexChart
from survey.exporter.tex.question2tex_raw import Question2TexRaw
from survey.exporter.tex.question2tex_sankey import Question2TexSankey
from survey.models.question import Question

LOGGER = logging.getLogger(__name__)


class Survey2Tex(Survey2X):

    ANALYSIS_FUNCTION = []

    def __init__(self, survey, configuration=None):
        Survey2X.__init__(self, survey)
        self.tconf = configuration

    def _synthesis(self, survey):
        """ Return a String of a synthesis of the report. """
        pass

    def _additional_analysis(self, survey, latex_file):
        """ Perform additional analysis. """
        for function_ in self.ANALYSIS_FUNCTION:
            LOGGER.info("Performing additional analysis with %s", function_)
            latex_file.text += function_(survey)

    def treat_question(self, question, survey):
        LOGGER.info("Treating, %s %s", question.pk, question.text)
        options = self.tconf.get(
            survey_name=self.survey.name, question_text=question.text
        )
        multiple_charts = options.get("multiple_charts")
        if not multiple_charts:
            multiple_charts = {"": options.get("chart")}
        question_synthesis = ""
        i = 0
        for chart_title, opts in list(multiple_charts.items()):
            i += 1
            if chart_title:
                # "" is False, by default we do not add section or anything
                mct = options["multiple_chart_type"]
                question_synthesis += "\%s{%s}" % (mct, chart_title)
            tex_type = opts.get("type")
            if tex_type == "raw":
                question_synthesis += Question2TexRaw(question, **opts).tex()
            elif tex_type == "sankey":
                other_question_text = opts["question"]
                other_question = Question.objects.get(text=other_question_text)
                q2tex = Question2TexSankey(question)
                question_synthesis += q2tex.tex(other_question)
            elif tex_type in ["pie", "cloud", "square", "polar"]:
                q2tex = Question2TexChart(question, latex_label=i, **opts)
                question_synthesis += q2tex.tex()
            elif locate(tex_type) is None:
                msg = "{} '{}' {}".format(
                    _("We could not render a chart because the type"),
                    tex_type,
                    _(
                        "is not a standard type nor the path to an "
                        "importable valid Question2Tex child class. "
                        "Choose between 'raw', 'sankey', 'pie', 'cloud', "
                        "'square', 'polar' or 'package.path.MyQuestion2Tex"
                        "CustomClass'"
                    ),
                )
                LOGGER.error(msg)
                question_synthesis += msg
            else:
                q2tex_class = locate(tex_type)
                # The use will probably know what type he should use in his
                # custom class
                opts["type"] = None
                q2tex = q2tex_class(question, latex_label=i, **opts)
                question_synthesis += q2tex.tex()
        section_title = Question2Tex.html2latex(question.text)
        return """
\\clearpage{}
\\section{%s}

\label{sec:%s}

%s

""" % (
            section_title,
            question.pk,
            question_synthesis,
        )

    def generate(self, path, output=None):
        """ Compile the pdf from the tex file. """
        dir_name, file_name = os.path.split(path)
        os.chdir(dir_name)
        os.system("xelatex {}".format(file_name))
        os.system("xelatex {}".format(file_name))
        if output is not None:
            os.system("mv {}.pdf {}".format(file_name[:-3], output))
        os.chdir(settings.ROOT)

    def survey_to_x(self, questions=None):
        if questions is None:
            questions = self.survey.questions.all()
        document_class = self.tconf.get("document_class", survey_name=self.survey.name)
        kwargs = self.tconf.get(survey_name=self.survey.name)
        del kwargs["document_class"]
        ltxf = LatexFile(document_class, **kwargs)
        self._synthesis(self.survey)
        for question in questions:
            ltxf.text += self.treat_question(question, self.survey)
        self._additional_analysis(self.survey, ltxf)
        return ltxf.document

    def generate_pdf(self):
        """ Compile the pdf from the tex file. """
        self.generate_file()
        self.generate(self.file_name())
