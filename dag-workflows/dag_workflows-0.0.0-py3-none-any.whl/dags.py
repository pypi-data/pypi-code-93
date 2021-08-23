"""
Read transformations from a folder
"""
import importlib.util
import logging
import os
import re

import yaml

from workflows import bases

logger = logging.getLogger(__name__)


def register_directory(folder_path: str):
    """
    Given a folder, register all DAG folders inside it.
    """
    registry = bases.DagRegistry()
    for entry in os.scandir(folder_path):  # type: os.DirEntry
        if entry.is_dir():
            if entry.name in ("__pycache__",):
                continue  # skip
            try:
                registry[entry.name] = register_dag(entry.path)
                logger.debug("Registered DAG %s", entry.path)
            except Exception as exc:  # pylint: disable=too-broad-exception
                registry[entry.name] = exc
                logger.warning("Could not register DAG in %s: %s", entry.path, exc)

    registry.validate()
    return registry


def register_dag(folder_path: str) -> bases.DAG:
    """
    Given a folder, register it if it has a workflow.yaml file.
    """
    spec_file = os.path.join(folder_path, "workflow.yaml")
    if not os.path.isfile(spec_file):
        raise bases.RegistrationError(f"No workflow.yaml file found in {folder_path}")
    spec = yaml.safe_load(open(spec_file))
    dag = bases.DAG(folder=folder_path, **spec)

    for entry in os.scandir(folder_path):  # type: os.DirEntry
        if entry.is_file():
            if entry.name in ("__init__.py", ".DS_Store", "workflow.yaml"):
                continue  # skip non-transforms
            register_task(dag, entry.path)

    dag.validate()
    return dag


SQL_COMMENT = re.compile(r"/\*(.*)\*/", re.MULTILINE + re.DOTALL)


def register_task(dag: bases.DAG, file_path: str) -> None:
    """
    Load a transform file and add it to the DAG
    """
    if file_path.endswith(".py"):
        module_spec = importlib.util.spec_from_file_location("task", file_path)
        module = importlib.util.module_from_spec(module_spec)
        module_spec.loader.exec_module(module)
        spec = yaml.safe_load(module.__doc__)
        spec["run"] = module.run
    elif file_path.endswith(".sql"):
        sql = open(file_path).read()
        spec_text = SQL_COMMENT.match(sql)
        if not spec_text:
            raise bases.RegistrationError("Cannot find a YAML spec in file %s", file_path)
        spec = yaml.safe_load(spec_text.group(1))
        spec["sql"] = sql
    elif file_path.endswith(".yaml"):
        spec = yaml.safe_load(open(file_path))
    else:
        raise bases.RegistrationError("Unsupported file type: %s", file_path)

    task_type = spec.pop("type", None)
    if not task_type:
        raise bases.RegistrationError("`type` is a required field in task %s", file_path)
    task_class = bases.load_class(task_type, bases.TASK_TYPES)
    name = os.path.basename(file_path)
    task_class(dag=dag, name=name, **spec)
