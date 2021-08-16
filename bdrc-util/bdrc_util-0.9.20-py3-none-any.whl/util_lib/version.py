def bdrc_util_version() -> str:
    import pkg_resources  # part of setuptools
    return pkg_resources.require("bdrc-util")[0].version
