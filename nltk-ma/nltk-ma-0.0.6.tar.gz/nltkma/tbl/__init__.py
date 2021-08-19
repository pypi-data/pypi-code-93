# Natural Language Toolkit: Transformation-based learning
#
# Copyright (C) 2001-2021 NLTK Project
# Author: Marcus Uneson <marcus.uneson@gmail.com>
#   based on previous (nltk2) version by
#   Christopher Maloof, Edward Loper, Steven Bird
# URL: <http://nltk.org/>
# For license information, see  LICENSE.TXT

"""
Transformation Based Learning

A general purpose package for Transformation Based Learning,
currently used by nltk.tag.BrillTagger.
"""

from nltkma.tbl.template import Template

# API: Template(...), Template.expand(...)

from nltkma.tbl.feature import Feature

# API: Feature(...), Feature.expand(...)

from nltkma.tbl.rule import Rule

# API: Rule.format(...), Rule.templatetid

from nltkma.tbl.erroranalysis import error_list
