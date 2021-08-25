from enum import Enum
from parse import parse as fparse
from pathlib import Path
from yaml import dump
from os import sep as os_sep

SubclassablePathType = type(Path())

def check_yaml(yaml_dict, keys):
    "Validate keys of the YAML dict for a GitLab Pages CI config."
    for k in keys:
        assert k in yaml_dict, f"YAML missing key: '{k}'"

class Stage(Enum):
    "There are multiple possible stages but I think GLP just uses 'deploy'."
    #Build = "build"
    #Test = "test"
    Deploy = "deploy"

class Cmd(Enum):
    """
    Fixed strings to validate against (as an enum so as to be immutable and named),
    representing commands in a build script.  The `Cmd.Cp` command is templated,
    using "{}" which will be parsed by `parse` from the package `parse`, described
    as 'the opposite of format()' i.e. like f-strings in reverse.
    """
    Mk = "mkdir .public"
    Cp = "cp -r {}* .public"
    Mv = "mv .public public"
    Cu = "curl -X POST -F token={} -F ref={} https://gitlab.com/api/v4/projects/{}/trigger/pipeline"

class TemplateVarMixIn:
    def set_configured_var_name(self, var_name):
        self._configured_var_name = var_name

    def set_configured_value(self, val):
        self._configured_val = val

    @staticmethod
    def configure_var_str(configured_var):
        "Mask `None` values as the empty string (N.B. also will affect false-y values)"
        configured_str = f"{configured_var}" if configured_var else ""
        return configured_str

    @property
    def as_str(self):
        configured_var = self._configured_val
        configured_str = self.configure_var_str(configured_var)
        return configured_str

class NewTemplateVarMixIn(TemplateVarMixIn):
    def __new__(cls, val):
        return type(super()).__new__(cls, val)

class StrTV(str, NewTemplateVarMixIn):
    pass

class PathTV(SubclassablePathType, NewTemplateVarMixIn):
    @staticmethod
    def configure_var_str(configured_var):
        """
        Must take care not to accidentally let an empty path become the root path
        while ensuring that paths are otherwise always terminated by a path separator
        """
        configured_str = f"{configured_var}{os_sep}" if configured_var else ""
        return configured_str

class FmtCmd(dict):
    """
    A formatted template will take a string such as:

      "Hello {}, the date today is {} the {} of {}, {}."
    
    along with 1 or more [in this case 5] variable parts, each of which
    has a name, indicated by the keys of a dict. In this case it'd be:
    
      ["name", "day_of_week", "day_of_month", "month", "year"]

    The values corresponding to these keys in the dict would be `StrTV`
    objects, initialised with 2 pieces of info: the templated string and the
    callable to be applied after it has been parsed (or alternatively `None`).
    """
    def __init__(self, cmd, d):
        self._cmd = cmd
        self._key, *self._keys = d
        if self._keys:
            vars(self)["_keys"].insert(0, self._key)
        vars(self).update({f"_key{'s' if not self._keys else ''}": None})
        # So either (_key = None, _keys = list) OR (_key = string, _keys = None)
        super().__init__(d)

    @property
    def formatted_cmd(self):
        cmd = self._cmd.value # template string (from the Cmd enum)
        vals = self.configured_values.values() # set by Script.parse on __init__
        # vals is a list of either: None (no match), or TemplateVarMixIn-inheritor
        #strings = [v.as_str if v else "" for v in vals]
        strings = []
        formatted = cmd.format(*[v.as_str if v else "" for v in vals])
        return formatted

    def set_configured_values(self, val_list):
        for k, val in zip(self, val_list):
            if val:
                template_var = val
                template_var.set_configured_var_name(k) # not needed, just for debugging
                template_var.set_configured_value(val)
        self._configured_values = dict(zip(self, val_list)) # {var_name:TemplateVarMixIn}

    @property
    def configured_values(self):
        return self._configured_values

class Script:
    """
    The script (list of commands) to run, relating to serving files from a
    single directory (which must be named 'public').
    """
    def __init__(self, cmd_list):
        self.cfg = {}
        self.parsed_templates = []
        self.parse(cmd_list)

    templates = {
        Cmd.Mk: None,
        Cmd.Cp: {
            "subdirectory": PathTV
        },
        Cmd.Mv: None,
        Cmd.Cu: ["token", "ref", "project_id"], # will default to TemplateVar callback
    }

    def parse(self, commands, default_callback=StrTV):
        for i, command in enumerate(commands):
            template_cmd = [*self.templates][i]
            d = self.templates.get(template_cmd) # indicates how to interpret template
            if d:
                # Extract the variable command from template_cmd and parse against
                # command (i.e. the full string from file) applying any callback
                if type(d) is list:
                    # Check if type(d) is list, apply default callback if so
                    d = {k: default_callback for k in d}
                    # Change it so you can reuse it later (in `as_list`) as a dict
                    self.templates[template_cmd] = d # template_cmd used as dict key
                fmt = FmtCmd(template_cmd, d) # store template_cmd as attrib on d
                self.parse_formatted_template(fmt, command)
                fmt.set_configured_values([self.cfg.get(k) for k in fmt])
                self.parsed_templates.append(fmt)
            else:
                # Fixed templated string (no variable part to process), just validate it
                match_str = f"{template_cmd.value=} == {command=}"
                assert template_cmd.value == command, f"Match failed: {match_str}"
                self.parsed_templates.append(template_cmd)

    def parse_formatted_template(self, fmt, command):
        template_cmd = fmt._cmd
        configured_value = fparse(template_cmd.value, command)
        if configured_value:
            vals = configured_value.fixed
        else:
            if len(fmt) == 1:
                vals = [None]
            else:
                e_msg = ("Cannot distinguish empty values for a command template"
                " with multiple variable parts.\nTODO: handle if needed, i.e. if "
                "multiple parts can vary and it is valid for them to potentially be "
                "empty (for now it is invalid for any of the multi-parts to be blank)")
                raise NotImplementedError(e_msg)
                # Previously the code below ran, but this cannot distinguish one from
                # multiple empty/missing values, and will 'blank' the provided ones too
                vals = [None for k in fmt]
        for val, (k, callback) in zip(vals, fmt.items()):
            assert k not in self.cfg, "Key {k} already seen: aborting! Oh no!"
            if val and callable(callback):
                val = callback(val) # call the supplied function on the parsed value
            self.cfg.update({k: val})

    @property
    def as_list(self):
        cmd_list = []
        for t in self.parsed_templates:
            if isinstance(t, FmtCmd):
                cmd_list.append(t.formatted_cmd)
            elif isinstance(t, Cmd):
                # Fixed template string, just pass its [string] value
                cmd_list.append(t.value)
            else:
                raise TypeError(f"Unexpected command '{t=}' in parsed_templates")
        return cmd_list

    def __repr__(self):
        if not (subdir := self.cfg.get("subdirectory")):
            subdir = ""
        script_repr = " ".join(f"{k}='{v}'" for k,v in self.cfg.items())
        return f"Script <{script_repr}>"

class Artifacts:
    """
    Build artifacts means things not tracked by git to be attached,
    i.e. the 'public' directory created during the Pages build.
    """
    def __init__(self, yaml_dict):
        assert "paths" in yaml_dict, "No paths artifact"
        paths = ["public"]
        self.paths = paths
        assert yaml_dict.get("paths") == paths, f"No artifact {paths=}"

    @property
    def as_dict(self):
        return {"paths": self.paths}

    def __repr__(self):
        cls = self.__class__.__name__
        paths = self.paths
        return f"{cls} <{paths=}>"

class Only:
    "Only run on the master branch (or else specify which `branch`)"
    def __init__(self, yaml_entry, branch="master"):
        assert yaml_entry == [branch], f"No path artifact {branch}"
        self.branch = [branch]

    def __repr__(self):
        cls = self.__class__.__name__
        branch = self.branch
        return f"{cls} <{branch=}>"

class PagesJob:
    "Required to build GitLab Pages: validates YAML and stores as object"
    def __init__(self, yaml_dict):
        check_yaml(yaml_dict, ["stage", "script", "artifacts", "only"])
        self.stage = Stage(yaml_dict.get("stage"))
        self.script = Script(yaml_dict.get("script"))
        self.artifacts = Artifacts(yaml_dict.get("artifacts"))
        self.only = Only(yaml_dict.get("only"))

    @property
    def as_dict(self):
        d = {
            "stage": self.stage.value,
            "script": self.script.as_list,
            "artifacts": self.artifacts.as_dict,
            "only": self.only.branch
        }
        return d
    
    def __repr__(self):
        cls = self.__class__.__name__
        return f"{cls}: {{{self.stage}, {self.script}, {self.artifacts}, {self.only}}}"

class SiteCI:
    "Representing (and validating) a `gitlab-ci.yml` config deployed to GitLab Pages."
    def __init__(self, yaml_dict):
        check_yaml(yaml_dict, ["pages"])
        self.pages = PagesJob(yaml_dict.get("pages"))

    @property
    def pages(self):
        return self._pages

    @pages.setter
    def pages(self, pages):
        self._pages = pages

    def __repr__(self):
        cls = self.__class__.__name__
        return f"{cls}: {self.pages}"

    @property
    def as_dict(self):
        return {"pages": self.pages.as_dict}

    @property
    def as_yaml(self):
        return dump(self.as_dict, sort_keys=False)
