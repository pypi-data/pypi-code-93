import os
from string import Template
from typing import Any, Dict, List, Union

import attr

"""
Functions to create directory (and files) structure easily

see also:
- https://stackoverflow.com/questions/26288551/render-json-to-directory-structure-in-python

"""


def _file_description_action_converter(actions):
    if isinstance(actions, str):
        return [file_actions_map[actions]()]
    elif isinstance(actions, FileAction):
        return [actions]
    elif isinstance(actions, list):
        new_actions = []
        for action in actions:
            if isinstance(action, str):
                action = FileAction()
            elif isinstance(action, FileAction):
                pass
            else:
                raise TypeError(
                    f"actions must be of type 'str' or {FileAction.__name__!r}"
                )
            new_actions.append(action)
        return actions
    else:
        raise TypeError(
            f"actions must be of type 'str' or {FileAction.__name__!r} or list"
        )


@attr.s
class FileDescription:
    """Used to describe file to create the home structure"""

    name = attr.ib()
    src = attr.ib(default=None)
    content = attr.ib(default="")
    substitute = attr.ib(default=False)
    actions = attr.ib(
        default=attr.Factory(list), converter=_file_description_action_converter
    )


@attr.s
class NormalizedFile:
    """Normalize FileDescription"""

    path = attr.ib()
    content = attr.ib()
    framework = attr.ib()


def normalize_file_description(
    file_description: FileDescription, parent_path, framework
):
    # FIXME: handle the case of big files (copy by chunk)? and test it
    # FIXME: when we have a source file? do we need to copy the permissions?
    # get the content of the file
    if file_description.src:
        # from a source file
        with open(file_description.src) as f:
            content = f.read()
    else:
        content = file_description.content
    # substitute variables
    # TODO: add general substitute variable in the framework to default to
    if file_description.substitute:
        content = Template(content).substitute(framework.get_variables())

    path = os.path.join(parent_path, file_description.name)
    return NormalizedFile(path, content, framework)


@attr.s
class DirectoryDescription:
    """Used to describe directory to create the home structure"""

    name = attr.ib()
    nodes = attr.ib(default=attr.Factory(list))


# ======= #
# ACTIONS #
# ======= #


class FileAction:
    """Hook when creating files"""

    def before_normalize(self, file_description: FileDescription, framework):
        pass

    def after_normalize(self, normalized_file: NormalizedFile):
        pass

    def after_creation(self, normalized_file: NormalizedFile):
        pass

    def uninstall(self, file: FileDescription, framework):
        pass


class BashrcFileAction(FileAction):
    """To alter file content/name/"""

    _add_to_bashrc_template = """\n# Execute the '{basename}' bash file of '{framework_name}'
if [ -f {path} ]; then
    . {path}
fi
"""

    def __init__(self, bashrcpath=None):
        if bashrcpath is None:
            bashrcpath = os.path.join(os.path.expanduser("~"), ".bashrc")
        self.bashrcpath = bashrcpath
        self.added_bashrc = None

    def _get_add_to_bashrc(self, file: NormalizedFile):
        basename = os.path.basename(file.path)
        return self._add_to_bashrc_template.format(
            basename=basename, path=file.path, framework_name=file.framework.name
        )

    def after_normalize(self, file: NormalizedFile):

        with open(self.bashrcpath) as f:
            bashrc = f.read()

        add_to_bashrc = self._get_add_to_bashrc(file)

        if add_to_bashrc not in bashrc:
            with open(self.bashrcpath, "a") as f:
                f.write(add_to_bashrc)
        # store added_bashrc to be able to uninstall it
        self.added_bashrc = add_to_bashrc

    def uninstall(self, file_description, framework):
        """Remove the added lines in the bashrc file"""
        # FIXME: uninstall can be called in the same execution when the file is created
        # or it can be called in an other execution, so the self.added_bashrc could not be
        # intiialised and be None, added_bashrc must be deduced.
        with open(self.bashrcpath) as f:
            bashrc = f.read()
        # if self.added_bashrc in bashrc:
        #    bashrc = bashrc.replace(self.added_bashrc, "")

        with open(self.bashrcpath, "w") as f:
            f.write(bashrc)


file_actions_map = {"bashrc": BashrcFileAction}
"""
Differents actions:
- bashrc: point ~/.bashrc to execute this script
- for eachfile
    - run prehook on File
    - normalize File to NormalizedFile
    - run hook on NormalizedFile

init_home steps
- normalize home to a list of File and Directory (recursively)
-


"""


# TODO: add uninstall (remove every thing init did) (folders, databases, actions, ...)
def normalize_home_structure(
    nodes,
) -> List[Union[FileDescription, DirectoryDescription]]:
    if isinstance(nodes, list):
        return _normalize_home_nodes_list(nodes)
    elif isinstance(nodes, dict):
        return _normalize_home_nodes_dict(nodes)
    return nodes


def _normalize_home_nodes_list(
    nodes: List[str],
) -> List[Union[FileDescription, DirectoryDescription]]:
    normalized_nodes = []
    for node in nodes:
        if isinstance(node, str):
            # TODO: check if it contains "/"
            if node[-1] == "/":
                new_node = DirectoryDescription(node[:-1])
            else:
                new_node = FileDescription(node)
        else:
            new_node = node
        normalized_nodes.append(new_node)
    return normalized_nodes


def _normalize_home_nodes_dict(
    nodes: Dict[str, Any]
) -> List[Union[FileDescription, DirectoryDescription]]:
    normalized_nodes = []
    for name, value in nodes.items():
        if isinstance(value, str):
            new_node = FileDescription(name, content=value)
        elif isinstance(value, dict):
            new_node = DirectoryDescription(name, _normalize_home_nodes_dict(value))
        if isinstance(node, str):
            # TODO: check if it contains "/"
            if node[-1] == "/":
                new_node = DirectoryDescription(node[:-1])
            else:
                new_node = FileDescription(node)
        else:
            new_node = node
        normalized_nodes.append(new_node)
    return normalized_nodes


"""
class File:
    def __init__(self, name: str, src=None, content=None):
        self.name = name
        self.src = src
        if content is None:
            content = ""
        self.content = content


class D:
    def __init__(self, name, *nodes):
        self.name = name
        self.nodes = nodes
"""
