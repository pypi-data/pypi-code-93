# Copyright 2020 Sushil Khanchi <sushilkhanchi97@gmail.com>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
#
# SPDX-License-Identifier: GPL-2.0-or-later
from heptapod.gitlab.tag import (
    gitlab_tag_ref,
)


def iter_gitlab_tags_as_refs(tags):
    """Iterate on given tags, yielding full Git refs."""
    for tag in tags:
        yield gitlab_tag_ref(tag)
