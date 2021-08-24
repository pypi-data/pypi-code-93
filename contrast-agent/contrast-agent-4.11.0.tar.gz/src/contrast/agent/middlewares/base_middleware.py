# -*- coding: utf-8 -*-
# Copyright © 2021 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from __future__ import print_function

import platform
import sys

from contrast import __version__, AGENT_CURR_WORKING_DIR
from contrast.agent.patch_controller import disable_assess_patches
from contrast.agent import patch_controller, service_client, scope
from contrast.agent.policy.loader import Policy
from contrast.agent.assess.policy import trigger_policy
from contrast.agent.assess.preflight import update_preflight_hashes
from contrast.agent.assess.rules.providers.enable import enable_providers
from contrast.agent.middlewares.route_coverage.routes_mixin import RoutesMixin
from contrast.agent.settings_state import SettingsState
from contrast.agent.speedracer_input_analysis import get_input_analysis
from contrast.api.dtm_pb2 import AttackResult
from contrast.utils.decorators import cached_property
from contrast.utils.exceptions.contrast_service_exception import (
    ContrastServiceException,
)
from contrast.utils.string_utils import truncate
from contrast.extern.six import PY2
from contrast.utils.decorators import log_time_cm
from contrast.utils.exceptions.security_exception import SecurityException
from contrast.utils.library_reader.library_reader import LibraryReader
from contrast.utils.loggers.logger import setup_agent_logger, setup_basic_agent_logger
from contrast.utils.timer import now_ms_float, now_ms

# initialize a basic logger until config is parsed
logger = setup_basic_agent_logger()


class BaseMiddleware(RoutesMixin):
    """
    BaseMiddleware contains all the initial setup for the framework middlewares

    Requirements:

        1. It's callable
        2. It has call_with_agent
        3. It has call_without_agent

    Pre and post filter calls should not block the flow that this class has.

    Pre -> get_response -> post
    """

    _loaded = False
    app_name = ""  # This should be overridden by child classes

    DIAGNOSTIC_ENDPOINT = "/save-contrast-security-config"
    DIAGNOSTIC_ALLOWED_SERVER = "localhost"
    DIAGNOSTIC_ALLOWED_IP = "127.0.0.1"
    OVERRIDE_MESSAGE = (
        "A security filter prevented original response from being returned."
    )
    LOGS_SEPARATOR = "-" * 120
    PY2_DEPRECATION_MSG = (
        "[Contrast Security] [DEPRECATION] Support for Python 2.7  will be removed in "
        "2021. Please contact Customer Support prior if you require continued support."
    )

    def __init__(self):
        # use _loaded to call our middleware only once because of runserver and
        # WSGIHandler being initialized twice.
        if BaseMiddleware._loaded:
            # TODO: PYT-1668 allow multiple middleware inits
            logger.warning(
                "Contrast Agent middleware initialized more than once per process."
            )
            return

        # id to distinguish middlewares created by different processes
        self.id = id(self)

        self.log_deprecation()
        self.log_initialize()

        self.settings = None

        self.routes = {}
        self.first_request = True

        if not self.initialize_settings(self.app_name):
            logger.error("Unable to initialize Contrast Agent.")
            return

        if not self.settings.is_agent_config_enabled():
            logger.warning("Contrast Agent is not enabled.")
            return

        setup_agent_logger(self.settings.config)
        self.settings.config.log_config()

        if not self.initialize_service_client():
            logger.error("Unable to initialize Contrast Agent.")
            return

        # This call must happen after initializing SR so we have all data to log
        self.log_environment()
        self.warn_for_misleading_config()

        self.initialize_libraries()

        patch_controller.enable_patches()

        if self.settings.is_assess_enabled():
            # For now agent runtime starts before config scanning
            # this will be reset when time_limit_threshold is reached,
            # it doesn't simbolize the total agent runtime for all time.
            self.settings.agent_runtime_window = now_ms()

            enable_providers()
            self.scan_configs()

        self.log_finish_initialize()

        self.request_start_time = None
        BaseMiddleware._loaded = True

    def initialize_settings(self, app_name):
        """
        Initialize agent settings.

        Returns True on settings being initialized and False if any failure.
        """
        try:
            self.settings = SettingsState(app_name=app_name)
        except Exception as e:
            logger.error(e)
            return False
        return True

    def initialize_service_client(self):
        """
        Initialize connection to service.

        Returns True on service being initialized and False if any failure.
        """
        try:
            service_client.send_startup_messages()
        except (Exception, ContrastServiceException) as e:
            logger.error(e)
            return False
        return True

    def warn_for_misleading_config(self):
        protect_enabled = self.settings.is_protect_enabled()
        assess_enabled = self.settings.is_assess_enabled()

        logger.info("Protect: %s", protect_enabled)
        logger.info("Assess: %s", assess_enabled)

        if protect_enabled and self.settings.config.get("assess.enable"):
            logger.warning("Protect is running but Assess is enabled in local config")
            logger.warning("Defaulting to Protect behavior only")

        if not protect_enabled and self.settings.config.get("protect.enable", True):
            logger.warning("Protect enabled in local config but disabled by Teamserver")

        if (
            self.settings.is_agent_config_enabled()
            and not protect_enabled
            and not assess_enabled
        ):
            logger.warning("Neither Protect nor Assess is running")

    def log_environment(self):
        """
        Log current working directory, python version and pip version
        """
        banner = "{0}ENVIRONMENT{0}".format("-" * 50)
        logger.debug(banner)
        logger.debug("Current Working Dir: %s", AGENT_CURR_WORKING_DIR)
        logger.debug("Python Version: %s", sys.version)
        logger.debug("Framework Version: %s", self.settings.framework)
        logger.debug("Contrast Python Agent Version: %s", __version__)
        logger.debug(
            "Contrast Service Version %s",
            self.settings.server_features.contrast_service,
        )
        logger.debug("Platform %s", platform.platform())

        try:
            import pip

            logger.debug("Pip Version: %s", pip.__version__)
        except:
            pass

        logger.debug(banner)

    def initialize_libraries(self):
        """
        If enabled, read libraries from the application
        :return: True
        """
        if not self.settings.is_analyze_libs_enabled():
            return

        # Passing callback to send message due to a circular import issue, and a
        # deadlock occurring if something is imported inside of a function running in
        # this thread
        self.library_reader = LibraryReader(
            send_message_func=service_client.send_messages
        )
        self.library_reader.start_library_analysis_thread()

    def is_agent_enabled(self):
        """
        Agent is considered enabled if all of the following are true:
        1. config value for 'enable' is True (or empty, defaults to True)
            (meaning no errors during initialization process including initial
            connection to Speedracer)
        2. ServiceClient connection to Speedracer is True

        NOTE: If #3 is false (the connection to Speedracer is down at any time during
        the request cycle) then the agent is automatically disabled.
        """
        if self.settings is None:
            return False

        if not self.settings.is_agent_config_enabled():
            return False

        if not service_client.is_connected():
            try:
                service_client.send_startup_messages()
            except ContrastServiceException:
                return False

        return service_client.is_connected()

    def call_with_agent(self, context, environ, start_response):
        pass

    def call_without_agent(self):
        """
        If Agent is either disabled or not initialized due to either entire settings
        initialization failing or just loggers failing, then we should print to stdout
        that the Agent is not running.

        In the case of the agent is disabled by a reaction from SR, we have to disable
        assess patches here because checking for context inside of our builtin string
        patches is much more expensive to do since they are called very frequently.

        The agent does not set context when this function is called so all other patches
        (e.g propagators) that check context shouldn't run.
        """
        disable_assess_patches()

        logger.warning("Contrast Agent is not running.")

    def handle_ensure(self, context, request):
        """
        Method that should run for all middlewares AFTER every request is made.
        """
        if context is None:
            logger.error("Context not defined in middleware ensure")
            return

        with scope.contrast_scope():
            if self.settings.is_assess_enabled():
                # route discovery and storage needs to occur before sending messages
                self.handle_routes(context, request)

                logger.debug("Updating preflight hashes with route info")
                update_preflight_hashes(context)

            logger.debug("Sending final messages for reporting.")

            service_client.send_messages(self.final_messages(context))

    def final_messages(self, context):
        # Request body is truncated to not overwhelm ContrastUI.
        raw_request_body = context.activity.http_request.request_body_binary
        context.activity.http_request.request_body_binary = truncate(
            raw_request_body, length=4096
        )

        final_messages = [
            context.server_activity,
            context.activity,
        ]

        # Currently we do not report an observed route if the route signature is empty.
        # As a team we've decided there isn't a meaningful default signature value
        # we can provide to customers. If a route doesn't show up in Contrast UI,
        # it may be due to its missing signature. In this scenario, we will have to work
        # with the customer directly to understand why the signature was not created.
        if self.settings.is_assess_enabled() and context.observed_route.signature:
            final_messages.append(context.observed_route)

        if self.first_request:
            # ApplicationUpdate message only sent at first request once we have routes
            final_messages.append(service_client.build_update_message(self.routes))
            self.first_request = False

        return final_messages

    def generate_security_exception_response(self):
        """
        Generate a response to be returned in the case of a SecurityException.

        Middlewares must override this method in order to provide the kind
        of response object that is expected by that framework.
        """
        raise NotImplementedError(
            "Middlewares must provide their own security response generator"
        )

    def handle_exception(self, exception):
        """
        Handle an exception being thrown especially if it is a SecurityException
        """
        logger.debug(
            "Handling %s raised in %s",
            exception.__class__.__name__,
            self.__class__.__name__,
        )
        if isinstance(exception, SecurityException):
            logger.info("%s: %s", exception.__class__.__name__, exception)
            logger.debug("Overriding response in Contrast Middleware")
            return self.generate_security_exception_response()

        logger.error("Reraising %r", exception)
        raise

    def prefilter(self, context):
        """
        Prefilter - AKA input analysis - is performed mostly in Speedracer but partly
        in the agent.

        This is PROTECT only.

        In this method we call on speedracer to do input analysis, which can result in:
        1. Speedracer finds an attack in which case we block the request
        2. Speedracer returns input analysis to use for later sink / infilter analysis,
            in which case we store it here in the request context.
        """
        if not self.settings.is_protect_enabled():
            return

        with log_time_cm("protect prefilter"):
            context.speedracer_input_analysis = get_input_analysis()
            self.agent_prefilter()

    def agent_prefilter(self):
        """
        Prefilter for any rules that do not yet use speedracer
        """
        scope.enter_contrast_scope()
        try:
            self.prefilter_defend()
        except SecurityException:
            logger.exception("PROTECT: threw security exception in prefilter")
            raise
        except:
            logger.exception("PROTECT: threw exception in prefilter")
        finally:
            scope.exit_contrast_scope()

    def prefilter_defend(self):
        rules = self.settings.defend_rules
        logger.debug("PROTECT: Running Agent prefilter.")

        for rule in rules.values():
            is_prefilter = rule.is_prefilter()

            if is_prefilter:
                rule.prefilter()

    def postfilter(self, context):
        """
        For all postfilter enabled rules.
        """
        with log_time_cm("postfilter"):
            if self.settings.is_protect_enabled():
                try:
                    self.postfilter_defend()
                except SecurityException as e:
                    logger.exception("PROTECT: threw security exception in postfilter")
                    raise e
                except Exception:
                    logger.exception("PROTECT: threw exception in postfilter")

            if self.settings.is_assess_enabled():
                scope.enter_contrast_scope()
                try:
                    self.postfilter_assess(context)
                except Exception:
                    logger.exception("ASSESS: threw exception in postfilter")
                scope.exit_contrast_scope()

    def _process_trigger_handler(self, handler):
        """
        Gather metadata about response handler callback for xss trigger node

        We need to check whether the response handler callback is an instance method or
        not. This affects the way that our policy machinery works, and it also affects
        reporting, so we need to make sure to account for the possibility that handler
        is a method of some class rather than a standalone function.

        This should be called by the `trigger_node` method in child classes.
        """
        module = handler.__module__
        class_name = ""

        if hasattr(handler, "__self__"):
            class_name = handler.__self__.__class__.__name__
            args = (handler.__self__,)
            instance_method = True
        else:
            args = ()
            instance_method = False

        return module, class_name, args, instance_method

    @cached_property
    def trigger_node(self):
        """
        Trigger node property used by assess reflected xss postfilter rule

        This must be overridden by child classes that make use of the reflected
        xss postfilter rule.
        """
        raise NotImplementedError("Children must define trigger_node property")

    def assess_reflected_xss_postfilter(self, context):
        """
        Evaluate xss rule for assess

        The xss rule is applied to the response body in order to determine whether it
        contains untrusted data. We rely on propagation through any template rendering
        and through the framework. The expectation is that untrusted data from
        a request will propagate successfully all the way to the response body, which
        we are able to see here.

        Each child middleware class must implement specific logic for the trigger node
        since the reporting will differ between frameworks.
        """
        policy = Policy()

        rule = policy.triggers["reflected-xss"]

        # We need to exit scope here in order to account for the fact that some
        # frameworks evaluate the content lazily. We don't want to be in scope when
        # that occurs since it would make us lose propagation. This would prevent us
        # from seeing the response as a tracked string, which we require in order to
        # apply the rule.
        with scope.pop_contrast_scope():
            result = context.response.body

        trigger_node, args = self.trigger_node

        # TODO: PYT-721 this trigger scope is already and shouldn't be required.
        # If/when we consolidate all scope levels, this scope should be removed
        # entirely since the postfilter is already in scope when it's called.
        with scope.trigger_scope():
            trigger_policy.apply(rule, [trigger_node], result, args, {})

    def postfilter_assess(self, context):
        """
        Run postfilter for any assess rules. Reflected xss rule runs by default.
        May be overridden in child classes.

        If the response content type matches a allowed content type, do not run
        xss postfilter assess This is because the security team
        considers reflected xss within these content types to be a false positive.
        """
        logger.debug("ASSESS: Running Agent postfilter.")

        # it is possible other forms (capital case) variants exist
        accepted_xss_response_content_types = [
            "/csv",
            "/javascript",
            "/json",
            "/pdf",
            "/x-javascript",
            "/x-json",
            "/plain",
        ]

        content_type = context.response.headers.get("content-type", "")

        if not any(
            [
                name
                for name in accepted_xss_response_content_types
                if name in content_type
            ]
        ):
            self.assess_reflected_xss_postfilter(context)

    def postfilter_defend(self):
        rules = self.settings.defend_rules
        logger.debug("PROTECT: Running Agent postfilter.")

        for rule in rules.values():
            if rule.is_postfilter():
                rule.postfilter()

    def check_for_blocked(self, context):
        """
        Checks for BLOCK events in case SecurityException was caught by app code

        This should be called by each middleware after the view is generated
        but before returning the response (it can be before or after
        postfilter).

        If we make it to this call, it implies that either no SecurityException
        occurred, or if one did occur, it was caught by the application. If we
        find a BLOCK here, it necessarily implies that an attack was detected
        in the application, but the application caught our exception. If the
        application hadn't caught our exception, we never would have made it
        this far because the exception would have already bubbled up to the
        middleware exception handler. So this is really our first and our last
        opportunity to check for this particular edge case.
        """
        for result in context.activity.results:
            if result.response == AttackResult.BLOCKED:
                msg = "Rule {} threw a security exception".format(result.rule_id)
                raise SecurityException(None, message=msg)

    def log_start_request_analysis(self, request_path):
        self.request_start_time = now_ms_float()
        logger.debug("Beginning request analysis", request_path=request_path)

    def log_end_request_analysis(self, request_path):
        request_end_time = now_ms_float()

        logger.debug(
            "Ending request analysis",
            request_path=request_path,
        )

        elapsed_time = request_end_time - self.request_start_time

        logger.debug(
            "elapsed time request analysis ms",
            elapsed_time=elapsed_time,
            request_path=request_path,
        )

    def log_deprecation(self):
        if PY2:
            warn_color = "\033[91m"
            end_color = "\033[0m"
            print("\n{}{}{}\n".format(warn_color, self.PY2_DEPRECATION_MSG, end_color))
            logger.warning(self.PY2_DEPRECATION_MSG)

    def log_initialize(self):
        logger.info(
            "Initializing Contrast Agent %s [id=%s]", self.__class__.__name__, self.id
        )

        logger.info("Contrast Python Agent Version: %s\n", __version__)

    def log_finish_initialize(self):
        logger.info(
            "Finished Initializing Contrast Agent %s [id=%s] \n\n%s\n",
            self.__class__.__name__,
            self.id,
            self.LOGS_SEPARATOR,
        )

    def scan_configs(self):
        """
        Run config scanning rules for assess

        Not all frameworks we support will necessarily have config scanning rules.
        Those that do should override this method.
        """
        logger.debug("No config scanning rules for %s", self.__class__.__name__)
