from collections import namedtuple
import os

from contrast import AGENT_CURR_WORKING_DIR
import contrast.utils.configuration_utils as utils

from contrast.utils.loggers import DEFAULT_PROGNAME
from contrast.extern import structlog as logging

logger = logging.getLogger("contrast")

SPLIT_CWD = AGENT_CURR_WORKING_DIR.split(os.sep)
APP_NAME = SPLIT_CWD[len(SPLIT_CWD) - 1]
ENV_PREFIX = "CONTRAST"

ConfigOption = namedtuple("ConfigOption", ["name", "default_value", "type_cast"])


DEFAULT_SERVICE_HOST = "127.0.0.1"
DEFAULT_SERVICE_PORT = 30555


class AgentConfig(object):
    def __init__(self):
        self._config = utils.load_yaml_config()

        if not self._config:
            logger.info("No YAML config found; using default settings")
            self._config = {}

        self._config = utils.flatten_config(self._config)

        self.override_configs()

        # fallback for no host or no port specified
        # socket will still take precedence if it exists
        self.check_for_service_config()

    def get(self, key, default_value=None):
        return self._config.get(key, default_value)

    def put(self, key, value):
        if not key or key not in self._config:
            logger.error("Invalid contrast config option: %s", key)
            return

        self._config[key] = value

    def log_config(self):
        """Log configuration values EXCEPT API information containing sensitive data"""
        config_no_api = {
            key: self._config[key] for key in self._config if "api" not in key
        }

        logger.info("Current Configuration", **config_no_api)

    def override_configs(self):
        """
        For each class representing different parts of the config (Agent, etc),
        take the current config and apply any overriding logic such as overriding with
        environment keys/values.

        At this time the order of precedence is:
            os.env > Config yaml

        Meaning that a config value defined in os.environ must be used instead of
        the same config defined in contrast_security.yaml

        Note that CLI args (sys.argv) are not supported. This may change if the
        agent becomes a runner.
        """
        builders = [Agent, Application, Assess, Inventory, Protect, Root, Server]

        for builder in builders:
            builder().build(self._config)

    def check_for_service_config(self):
        """
        Check for and log user-provided config values for connecting to SR.
        Socket config takes precedence if it is user-provided. Otherwise assign
        host/port values if either is not provided.
        """
        socket_key = "agent.service.socket"
        host_key = "agent.service.host"
        port_key = "agent.service.port"

        # Socket is set
        if self.get(socket_key):
            logger.info(
                "Connecting to the Contrast Service using a UnixSocket socket: %s",
                self.get(socket_key),
            )
            return

        # Host and Port are set
        if self.get(host_key) and self.get(port_key):
            logger.info(
                "Connecting to the Contrast Service using a TCP socket: host: %s, port: %s",
                self.get(host_key),
                self.get(port_key),
            )
            return

        # Something is not set

        if self.get(host_key):
            self.put(port_key, DEFAULT_SERVICE_PORT)
            msg = "{} is not set. Falling back to default TCP socket host: {}, port: {}".format(
                port_key, self.get(host_key), self.get(port_key)
            )
        elif self.get(port_key):
            self.put(host_key, DEFAULT_SERVICE_HOST)
            msg = "{} is not set. Falling back to default TCP socket host: {}, port: {}".format(
                host_key, self.get(host_key), self.get(port_key)
            )
        else:
            self.put(host_key, DEFAULT_SERVICE_HOST)
            self.put(port_key, DEFAULT_SERVICE_PORT)
            msg = "Neither {} nor the pair of {} and {} are set. Falling back to default TCP socket host: {}, port: {}.".format(
                socket_key,
                host_key,
                port_key,
                self.get(host_key),
                self.get(port_key),
            )

        msg_prefix = "Missing a required connection value to the Contrast Service."
        warn_msg = "{} {}".format(msg_prefix, msg)

        logger.warning(warn_msg)

    def get_session_id(self):
        return self.get("application.session_id", "")

    def get_session_metadata(self):
        return self.get("application.session_metadata", "")


class ConfigBuilder(object):
    TOP_LEVEL = ""

    def __init__(self):
        self.default_options = []

    def build(self, config):
        """
        Given a dict config, iterate over the default_options and check if
        the corresponding config key/value should be either :
        1. replaced by an existing env var
        2. keep existing config key/val but type-cast the value
        3. add a new key/default_value to the config

        :param config: dict config
        :return: None, config dict is updated pass by reference
        """
        for option_name, default_val, type_cast in self.default_options:

            dot_alt = self._dot_alternative(option_name)
            underscore_alt = self._underscore_alternative(option_name)

            env_override = utils.get_env_key(underscore_alt)
            if env_override:
                # replace the config value with the os.env value and apply type-cast
                env_override = type_cast(env_override)
                config[dot_alt] = env_override
                continue

            if dot_alt in config:
                # update the config value with a type-cast value
                val = config[dot_alt]
                val = type_cast(val)
                config[dot_alt] = val
                continue

            # add a new key/default_value to config
            config[dot_alt] = default_val

    def _underscore_alternative(self, key):
        return "__".join(
            [x for x in [ENV_PREFIX, self.TOP_LEVEL, key.replace(".", "__")] if x]
        ).upper()

    def _dot_alternative(self, key):
        return ".".join([self.TOP_LEVEL, key]) if self.TOP_LEVEL else key


class Agent(ConfigBuilder):
    TOP_LEVEL = "agent"

    def __init__(self):
        super(Agent, self).__init__()

        self.default_options = [
            # Some logger default values are handled by the logger
            ConfigOption(
                name="logger.level",
                default_value="",
                type_cast=str,
            ),
            ConfigOption(name="logger.path", default_value="", type_cast=str),
            ConfigOption(
                name="logger.progname",
                default_value=DEFAULT_PROGNAME,
                type_cast=str,
            ),
            ConfigOption(
                name="python.enable_drf_response_analysis",
                default_value=True,
                type_cast=utils.str_to_bool,
            ),
            ConfigOption(
                name="python.enable_rep",
                default_value=True,
                type_cast=utils.str_to_bool,
            ),
            ConfigOption(
                name="python.assess.use_pure_python_hooks",
                default_value=False,
                type_cast=utils.str_to_bool,
            ),
            ConfigOption(
                name="polling.app_activity_ms", default_value=30000, type_cast=int
            ),
            ConfigOption(
                name="polling.server_activity_ms", default_value=30000, type_cast=int
            ),
            ConfigOption(
                name="polling.accumulated_rules_ms", default_value=30000, type_cast=int
            ),
            ConfigOption(
                name="service.enable", default_value=True, type_cast=utils.str_to_bool
            ),
            ConfigOption(name="service.host", default_value="", type_cast=str),
            ConfigOption(name="service.port", default_value="", type_cast=int),
            ConfigOption(name="service.socket", default_value="", type_cast=str),
        ]


class Application(ConfigBuilder):
    TOP_LEVEL = "application"

    def __init__(self):
        super(Application, self).__init__()

        self.default_options = [
            ConfigOption(name="code", default_value="", type_cast=str),
            ConfigOption(name="group", default_value="", type_cast=str),
            ConfigOption(name="metadata", default_value="", type_cast=str),
            ConfigOption(
                name="name",
                default_value=os.path.basename(AGENT_CURR_WORKING_DIR),
                type_cast=str,
            ),
            ConfigOption(name="path", default_value="", type_cast=str),
            ConfigOption(name="tags", default_value="", type_cast=str),
            ConfigOption(name="version", default_value="", type_cast=str),
            ConfigOption(name="session_id", default_value="", type_cast=str),
            ConfigOption(name="session_metadata", default_value="", type_cast=str),
        ]


class Assess(ConfigBuilder):
    TOP_LEVEL = "assess"

    def __init__(self):
        super(Assess, self).__init__()

        self.default_options = [
            ConfigOption(
                name="enable", default_value=None, type_cast=utils.str_to_bool
            ),
            ConfigOption(
                name="enable_scan_response",
                default_value=True,
                type_cast=utils.str_to_bool,
            ),
            ConfigOption(name="sampling.baseline", default_value=5, type_cast=int),
            ConfigOption(
                name="sampling.enable", default_value=True, type_cast=utils.str_to_bool
            ),
            ConfigOption(name="tags", default_value="", type_cast=str),
            ConfigOption(
                name="rules.disabled_rules",
                default_value=[],
                type_cast=utils.parse_disabled_rules,
            ),
            ConfigOption(
                name="stacktraces",
                default_value="ALL",
                type_cast=utils.parse_stacktraces_options,
            ),
            ConfigOption(
                name="max_context_source_events",
                default_value=100,
                type_cast=int,
            ),
            ConfigOption(
                name="max_propagation_events",
                default_value=250,
                type_cast=int,
            ),
            ConfigOption(
                name="time_limit_threshold",
                default_value=300000,  # 5 minutes in ms
                type_cast=int,
            ),
            ConfigOption(
                name="max_rule_reported",
                default_value=100,
                type_cast=int,
            ),
        ]


class Inventory(ConfigBuilder):
    TOP_LEVEL = "inventory"

    def __init__(self):
        super(Inventory, self).__init__()

        self.default_options = [
            ConfigOption(
                name="analyze_libraries",
                default_value=True,
                type_cast=utils.str_to_bool,
            ),
            ConfigOption(
                name="enable", default_value=True, type_cast=utils.str_to_bool
            ),
            ConfigOption(name="tags", default_value="", type_cast=str),
        ]


class Protect(ConfigBuilder):
    TOP_LEVEL = "protect"

    def __init__(self):
        super(Protect, self).__init__()

        self.default_options = [
            ConfigOption(
                name="enable", default_value=True, type_cast=utils.str_to_bool
            ),
            ConfigOption(name="samples.probed", default_value=50, type_cast=int),
            ConfigOption(name="samples.blocked", default_value=25, type_cast=int),
            ConfigOption(name="samples.exploited", default_value=100, type_cast=int),
            ConfigOption(
                name="samples.blocked_at_perimeter", default_value=25, type_cast=int
            ),
            ConfigOption(
                name="rules.bot-blocker.enable",
                default_value=False,
                type_cast=utils.str_to_bool,
            ),
            ConfigOption(
                name="rules.cmd-injection.detect_chained_commands",
                default_value=True,
                type_cast=utils.str_to_bool,
            ),
            ConfigOption(
                name="rules.cmd-injection.detect_parameter_command_backdoors",
                default_value=True,
                type_cast=utils.str_to_bool,
            ),
            ConfigOption(
                name="rules.cmd-injection.mode",
                default_value=None,
                type_cast=utils.protect_mode_to_protobuf,
            ),
            ConfigOption(
                name="rules.disabled_rules",
                default_value=[],
                type_cast=utils.parse_disabled_rules,
            ),
            ConfigOption(
                name="rules.method-tampering.mode",
                default_value=None,
                type_cast=utils.protect_mode_to_protobuf,
            ),
            ConfigOption(
                name="rules.nosql-injection.mode",
                default_value=None,
                type_cast=utils.protect_mode_to_protobuf,
            ),
            ConfigOption(
                name="rules.path-traversal.detect_common_file_exploits",
                default_value=True,
                type_cast=utils.str_to_bool,
            ),
            ConfigOption(
                name="rules.path-traversal.detect_custom_code_accessing_system_files",
                default_value=True,
                type_cast=utils.str_to_bool,
            ),
            ConfigOption(
                name="rules.path-traversal.mode",
                default_value=None,
                type_cast=utils.protect_mode_to_protobuf,
            ),
            ConfigOption(
                name="rules.reflected-xss.mode",
                default_value=None,
                type_cast=utils.protect_mode_to_protobuf,
            ),
            ConfigOption(
                name="rules.sql-injection.detect_chained_queries",
                default_value=True,
                type_cast=utils.str_to_bool,
            ),
            ConfigOption(
                name="rules.sql-injection.detect_dangerous_functions",
                default_value=True,
                type_cast=utils.str_to_bool,
            ),
            ConfigOption(
                name="rules.sql-injection.detect_suspicious_unions",
                default_value=True,
                type_cast=utils.str_to_bool,
            ),
            ConfigOption(
                name="rules.sql-injection.detect_tautologies",
                default_value=True,
                type_cast=utils.str_to_bool,
            ),
            ConfigOption(
                name="rules.sql-injection.mode",
                default_value=None,
                type_cast=utils.protect_mode_to_protobuf,
            ),
            ConfigOption(
                name="rules.ssrf.mode",
                default_value=None,
                type_cast=utils.protect_mode_to_protobuf,
            ),
            ConfigOption(
                name="rules.unsafe-file-upload.mode",
                default_value=None,
                type_cast=utils.protect_mode_to_protobuf,
            ),
            ConfigOption(
                name="rules.xxe.mode",
                default_value=None,
                type_cast=utils.protect_mode_to_protobuf,
            ),
        ]


class Server(ConfigBuilder):
    TOP_LEVEL = "server"

    def __init__(self):
        super(Server, self).__init__()

        self.default_options = [
            ConfigOption(
                name="name", default_value=utils.get_hostname(), type_cast=str
            ),
            ConfigOption(name="path", default_value="/", type_cast=str),
            ConfigOption(name="type", default_value="", type_cast=str),
            ConfigOption(name="version", default_value="", type_cast=str),
            ConfigOption(name="environment", default_value="", type_cast=str),
            ConfigOption(name="tags", default_value="", type_cast=str),
        ]


class Root(ConfigBuilder):
    TOP_LEVEL = None

    def __init__(self):
        super(Root, self).__init__()

        self.default_options = [
            ConfigOption(name="enable", default_value=True, type_cast=utils.str_to_bool)
        ]
