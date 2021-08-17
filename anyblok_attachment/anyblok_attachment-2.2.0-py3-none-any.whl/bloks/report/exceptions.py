# This file is a part of the AnyBlok / Attachment api project
#
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.


class TemplateException(Exception):
    """Simple exception if miss Template data"""


class PathException(Exception):
    """Simple exception if it is not a valid path for Template"""


class RenderException(Exception):
    """Simple exception for all error in the render method"""
