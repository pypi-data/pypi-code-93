#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2021  Stéphane Bard <stephane.bard@gmail.com>
#
# This file is part of hg_delivery
#
# hg_delivery is free software; you can redistribute it and/or modify it under
# the terms of the M.I.T License.
#


def to_int(*segment_names):
    """
       transform an request key param into an integer
       it can also deals with fizzle and transform tuple of string
       into tuple of integer
    """
    def predicate(info, request):
        """
           the function associate with to_int
        """
        match = info['match']
        for segment_name in segment_names:
            try:
                if isinstance(match[segment_name], (list, tuple)):
                    match[segment_name] = tuple(
                        [int(e) for e in match[segment_name]])
                else:
                    match[segment_name] = int(match[segment_name])
            except (TypeError, ValueError):
                pass
        return True
    return predicate
