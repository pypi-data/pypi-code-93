from typing import Optional

from tktl.core.loggers import LOG
from tktl.core.managers.project import ProjectManager


def init_project(path: Optional[str], name: str):
    project_path = ProjectManager.init_project(path, name)
    LOG.log(
        f"Project scaffolding created successfully at {project_path}", color="green",
    )
