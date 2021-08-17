import shutil

import pytest

from tktl.core.managers.project import ProjectManager


@pytest.fixture(scope="function")
def create_proj():
    ProjectManager.init_project(None, "sample_project")
    yield
    shutil.rmtree("sample_project")
