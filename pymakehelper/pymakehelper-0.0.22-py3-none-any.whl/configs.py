"""
All configurations for pymakehelper
"""


from pytconf import Config, ParamCreator


class ConfigVerbose(Config):
    """
    Parameters for verbosity
    """
    verbose = ParamCreator.create_bool(
        help_string="print the command?",
        default=False,
    )


class ConfigSymlinkInstall(Config):
    """
    Parameters for the symlink install tool
    """
    source_folder = ParamCreator.create_existing_folder(
        help_string="Which folder to install from?",
    )
    target_folder = ParamCreator.create_existing_folder(
        help_string="Which folder to install to?",
    )
    recurse = ParamCreator.create_bool(
        help_string="should I recurse?",
        default=True,
    )
    doit = ParamCreator.create_bool(
        help_string="actually perform the actions?",
        default=True,
    )
    debug = ParamCreator.create_bool(
        help_string="print what we are doing?",
        default=True,
    )
    force = ParamCreator.create_bool(
        help_string="remove target files if they are links?",
        default=True,
    )
