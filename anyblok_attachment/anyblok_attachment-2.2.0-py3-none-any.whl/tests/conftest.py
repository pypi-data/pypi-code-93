# This file is a part of the AnyBlok project
#
#    Copyright (C) 2019 Jean-Sebastien SUZANNE <js.suzanne@gmail.com>
#
# This Source Code Form is subject to the terms of the Mozilla Public License,
# v. 2.0. If a copy of the MPL was not distributed with this file,You can
# obtain one at http://mozilla.org/MPL/2.0/.
import pytest
from anyblok.tests.conftest import *  # noqa
from anyblok.tests.conftest import init_registry_with_bloks


@pytest.fixture(scope="function")
def registry_report_1(request, testbloks_loaded):
    registry = init_registry_with_bloks(['test_report_1'], None)
    request.addfinalizer(registry.close)
    return registry


@pytest.fixture(scope="function")
def registry_report_2(request, testbloks_loaded):
    registry = init_registry_with_bloks(['test_report_2'], None)
    request.addfinalizer(registry.close)
    return registry


@pytest.fixture(scope="function")
def registry_report_3(request, testbloks_loaded):
    registry = init_registry_with_bloks(['test_report_3'], None)
    request.addfinalizer(registry.close)
    return registry


@pytest.fixture(scope="class")
def registry_report_4(request, testbloks_loaded):
    registry = init_registry_with_bloks(['test_report_4'], None)
    request.addfinalizer(registry.close)
    return registry
