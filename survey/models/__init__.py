# -*- coding: utf-8 -*-

"""
    Permit to import everything from survey.models without knowing the details.
"""

import sys

from .answer import Answer
from .category import Category
from .question import Question
from .response import Response
from .survey import Survey

__all__ = ["Category", "Answer", "Category", "Response", "Survey", "Question"]
