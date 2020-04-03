# -*- coding: utf-8 -*-

import logging
from builtins import open
from datetime import datetime

LOGGER = logging.getLogger(__name__)


class LatexFile(object):

    """ Permit to handle the content of a LatexFile """

    def __init__(
        self,
        document_class,
        document_option=None,
        header=None,
        intro=None,
        footer=None,
        date=None,
        **kwargs
    ):
        LOGGER.debug(
            "Creating a document skeleton with document_class=%s, "
            "document_option=%s",
            document_class,
            document_option,
        )
        self.document_class = document_class
        self.text = ""
        self.document_option = self.set_value(document_option)
        self._header = self.set_value(header)
        self.intro = self.set_value(intro)
        self._footer = self.set_value(footer)
        if date is None:
            date = datetime.now().strftime("%B %d, %Y")
        self.date = date

    def set_value(self, value):
        """ Return the value we need for null text. """
        if value is None:
            return ""
        return value

    @property
    def header(self):
        """ Return the header of a .tex file.

        :rtype: String """
        header = "\\documentclass"
        if self.document_option:
            header += "[{}]".format(self.document_option)
        header += "{%s}\n" % self.document_class
        header += "\date{%s}\n" % self.date
        header += "%s\n" % self._header
        header += "\\begin{document}\n"
        header += "%s\n" % self.intro
        return header

    @property
    def footer(self):
        """ Return the footer of a .tex file.

        :rtype: String """
        end = """
\\end{document}
"""
        if self._footer:
            return self._footer + end
        else:
            return end

    def save(self, path):
        """ Save the document on disk. """
        with open(path, "wb") as tex_file:
            tex_file.write(self.document.encode("UTF-8"))

    @property
    def document(self):
        """ Return the full text of the LatexFile.

        :rtype: String"""
        return "{}{}{}".format(self.header, self.text, self.footer)
