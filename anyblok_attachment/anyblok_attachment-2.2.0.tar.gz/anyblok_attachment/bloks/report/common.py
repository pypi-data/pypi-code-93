# This file is a part of the AnyBlok / Attachment api project
#
#    Copyright (C) 2018 Jean-Sebastien SUZANNE <jssuzanne@anybox.fr>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
from anyblok.blok import BlokManager
from .exceptions import PathException
import os


def format_path(path):
    """Return the absolute path in function of the blok

    :param path: the path to format
    :return: the absolute path
    :exception: PathException
    """
    if '#=#' in path:
        blokname, path = path.split('#=#')
        path = os.path.join(BlokManager.getPath(blokname), path)

    if not os.path.exists(path):
        raise PathException("%s does not exists", path)

    return path
