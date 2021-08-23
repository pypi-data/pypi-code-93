# -*- coding: utf-8 -*-
#
# Copyright (C) 2021  Stéphane Bard <stephane.bard@gmail.com>
#
# This file is part of hg_delivery
#
# hg_delivery is free software; you can redistribute it and/or modify it under
# the terms of the M.I.T License.
#
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import MetaData

metadata = MetaData()
Base = declarative_base(metadata=metadata)
