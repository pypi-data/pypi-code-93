import json
import os
from pathlib import Path
import sys
from typing import BinaryIO
from zipfile import ZipFile

import click
from ntscli_cloud_lib.self_responder import SelfResponder
from ntscli_cloud_lib.sslconfig import SslConfig
from ntscli_cloud_lib.sslconfigmanager import SslConfigManager

# Implementation libs
import ntsjson
from ntsjson.functions import set_log_levels_of_libs
from ntsjson.log import logger, nts_verbosity_option


@click.group(name="ssl")
def ssl_group():
    """Test MQTT SSL broker configs"""


@ssl_group.command(name="list", short_help="List valid SSL configurations")
@nts_verbosity_option(logger, default=ntsjson.VERBOSE_DEFAULT_LEVEL, help=ntsjson.VERBOSE_HELP)
def ssl_list():
    """List the ssl configuration names."""
    set_log_levels_of_libs()
    mgr = SslConfigManager()
    names = [str(elt) for elt in list(mgr)]

    def checked_config(name):
        conf: SslConfig = mgr.get(name)
        shortened = Path(name).name
        if not conf.iscomplete():
            logger.debug(
                f"The filesystem entry {shortened} was in the ~/.config/netflix directory, but is not a valid SSL configuration directory "
                "for AWS IoT."
            )
            return None
        return shortened

    logger.info("Set -v debug for more information and help.")
    logger.info("Searching ~/.config/netflix/ for directories containing valid ssl configurations")
    logger.debug("Subdirectories of the ~/.config/netflix/ directory should be named configurations, such as 'cloud', 'test', etc.")
    logger.debug("The configuration directories should include the .pem, .crt, .json files provided by Netflix.")
    logger.debug(
        "The default configuration is named 'cloud', so for instance there should be a file located at ~/.config/netflix/cloud/host.json"
    )
    checked_names = [elt for elt in map(checked_config, names) if elt is not None]
    print(json.dumps(checked_names, indent=4))
    logger.info("Done")


@ssl_group.command(name="sanity", short_help="Offline check of SSL config")
@click.argument("name")
@nts_verbosity_option(logger, default=ntsjson.VERBOSE_DEFAULT_LEVEL, help=ntsjson.VERBOSE_HELP)
def ssl_sanity(name):
    """Offline sanity check a ssl configuration."""
    set_log_levels_of_libs()
    mgr = SslConfigManager()
    conf: SslConfig = mgr.get(name)
    if not mgr.has(name):
        logger.critical("That configuration wasn't found.")
        sys.exit(1)
    elif not conf.iscomplete():
        logger.error("The configuration exists, but is missing files. The following files must be present:")
        logger.error("cert.pem client.id host.json private.key rootca.crt")
        logger.error("If you got this configuration from Netflix, you may want to reach out to get a new copy.")
        sys.exit(1)
    else:
        print("Configuration passes basic offline checks.")


@ssl_group.command(name="selftest", short_help="Online pub/sub self test")
@click.argument("name")
@nts_verbosity_option(logger, default=ntsjson.VERBOSE_DEFAULT_LEVEL, help=ntsjson.VERBOSE_HELP)
def ssl_selftest(name):
    """Connect and do a basic pub/sub using a configuration."""
    set_log_levels_of_libs()
    logger.info("Set -v info or -v debug to show more traffic information.")
    mgr = SslConfigManager()
    conf: SslConfig = mgr.get(name)
    if not mgr.has(name):
        logger.critical("That configuration wasn't found.")
        sys.exit(1)
    elif not conf.iscomplete():
        logger.error("The configuration exists, but is missing files. The following files must be present:")
        logger.error("cert.pem client.id host.json private.key rootca.crt")
        sys.exit(1)

    responder = SelfResponder()
    try:
        responder.start(name)
    except ConnectionError as ce:
        logger.error(
            f"Failed to connect: {ce}\nBefore you file a help ticket with Netflix,\ncheck that your firewall allows you to reach "
            "the host and port in your SSL configuration directory through your firewall."
        )
        sys.exit(1)
    responder.check_request()
    responder.stop()

    print("Basic communication to this broker succeeded!")


@ssl_group.command(name="install", short_help="Install zip as certificate")
@click.option("--name", type=str, default="cloud", show_default=True, help="The destination config name")
@click.argument("source", type=click.File("rb"))
def ssl_install(name: str, source: BinaryIO):
    """Unzip, install, and perform an offline check of a zipped security certificate."""
    mgr = SslConfigManager()

    config_root = Path("~/.config/netflix").expanduser()
    if not config_root.exists():
        os.makedirs(config_root)

    with ZipFile(file=source) as source_zip:
        source_zip.extractall(path=mgr.dir / name)

    conf: SslConfig = mgr.get(name)
    if not mgr.has(name):
        logger.critical("We somehow failed to expand that directory.")
        sys.exit(1)
    elif not conf.iscomplete():
        logger.error("The new configuration was installed, but is missing files. The following files must be present:")
        logger.error("cert.pem client.id host.json private.key rootca.crt")
        sys.exit(1)
    else:
        print(f"The new configuration was installed at {str(mgr.dir / name)}")
