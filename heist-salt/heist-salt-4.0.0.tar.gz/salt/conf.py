CLI_CONFIG = {
    # The dyne will always be heist.
    # List the subcommands that will expose this option
    "key_plugin": {"subcommands": ["salt.minion"], "dyne": "heist"},
}
CONFIG = {
    # This will show up in hub.OPT.heist.key_plugin
    "key_plugin": {
        "default": "local_master",
        "help": "Define the salt key plugin to use.",
        "dyne": "heist",
    },
    "generate_keys": {
        "default": True,
        "action": "store_true",
        "help": "Generate the salt minions keys on the minion "
        "and copy over to the master",
        "dyne": "heist",
    },
    "retry_key_count": {
        "default": 5,
        "help": "Amount of times to retry accepting the salt-key,"
        "while the salt minion is still starting up",
        "dyne": "heist",
    },
    "salt_repo_url": {
        "default": "https://repo.saltproject.io/salt/singlebin/",
        "help": "The url to a repo that contains the repo.json/repo.mp"
        "file and the Salt artifacts",
        "dyne": "heist",
    },
}
SUBCOMMANDS = {"salt.minion": {"help": "", "dyne": "heist"}}
DYNE = {
    "artifact": ["artifact"],
    "heist": ["heist"],
    "salt": ["salt"],
    "service": ["service"],
    "tool": ["tool"],
}
