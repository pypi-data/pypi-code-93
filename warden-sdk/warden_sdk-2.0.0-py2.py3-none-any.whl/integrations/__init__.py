"""Central setup of integrations.

This module will load all of the integrations necessary for the initialized `warden_sdk`. Default integrations will always be loaded and supplementary integrations must be called when initializing the sdk.

  Typical usage example:

  from warden_sdk.integrations import setup_integrations
  setup_integrations(self.options["integrations"])
"""
from __future__ import absolute_import

from threading import Lock


from warden_sdk.utils import iteritems, logger
from typing import (Tuple)


_installer_lock = Lock()
_installed_integrations = set() 

def _generate_default_integrations_iterator(integrations, auto_enabling_integrations):
   """Generate list of Integrations.

   This function creates a list of imported integrations that are required, mainly the default integrations.

   Args:
      integrations: A list of integrations as functions.

   Returns:
      A list of integrations that have been imported, now ready to be setup.
   """

   def iter_default_integrations(with_auto_enabling_integrations):
      """Returns an iterator of the default integration classes:"""
      from importlib import import_module

      if with_auto_enabling_integrations:
         all_import_strings = integrations + auto_enabling_integrations
      else:
         all_import_strings = integrations

      for import_string in all_import_strings:
         try:
               module, cls = import_string.rsplit(".", 1)
               yield getattr(import_module(module), cls)
         except (DidNotEnable, SyntaxError) as e:
               logger.debug(
                  "Did not import default integration %s: %s", import_string, e
               )

   if isinstance(iter_default_integrations.__doc__, str):
      for import_string in integrations:
         iter_default_integrations.__doc__ += "\n- `{}`".format(import_string)

   return iter_default_integrations

_AUTO_ENABLING_INTEGRATIONS = (
   "warden_sdk.integrations.flask.FlaskIntegration",
   "warden_sdk.integrations.boto3.Boto3Integration",
)

iter_default_integrations = _generate_default_integrations_iterator(
   integrations=(
      "warden_sdk.integrations.logging.LoggingIntegration",
      "warden_sdk.integrations.excepthook.ExcepthookIntegration",
      "warden_sdk.integrations.awslambda.AwsLambdaIntegration",
      "warden_sdk.integrations.stdlib.StdlibIntegration",
      "warden_sdk.integrations.dedupe.DedupeIntegration",
      "warden_sdk.integrations.atexit.AtexitIntegration",
      "warden_sdk.integrations.modules.ModulesIntegration",
      "warden_sdk.integrations.argv.ArgvIntegration",
   ),
   auto_enabling_integrations=_AUTO_ENABLING_INTEGRATIONS
)
del _generate_default_integrations_iterator


def setup_integrations(
    integrations, with_defaults=True, with_auto_enabling_integrations=True
):
    """Given a list of integration instances this installs them all.  When
    `with_defaults` is set to `True` then all default integrations are added
    unless they were already provided before.
    """
    integrations = dict(
        (integration.identifier, integration) for integration in integrations or ()
    )

    logger.debug("Setting up integrations (with default = %s)", with_defaults)

    # Integrations that are not explicitly set up by the user.
    used_as_default_integration = set()

    if with_defaults:
        for integration_cls in iter_default_integrations(
            with_auto_enabling_integrations
        ):
            if integration_cls.identifier not in integrations:
                instance = integration_cls()
                integrations[instance.identifier] = instance
                used_as_default_integration.add(instance.identifier)

    for identifier, integration in iteritems(integrations):
        with _installer_lock:
            if identifier not in _installed_integrations:
                logger.debug(
                    "Setting up previously not enabled integration %s", identifier
                )
                try:
                    type(integration).setup_once()
                except NotImplementedError:
                    if getattr(integration, "install", None) is not None:
                        logger.warning(
                            "Integration %s: The install method is "
                            "deprecated. Use `setup_once`.",
                            identifier,
                        )
                        integration.install()
                    else:
                        raise
                except DidNotEnable as e:
                    if identifier not in used_as_default_integration:
                        raise

                    logger.debug(
                        "Did not enable default integration %s: %s", identifier, e
                    )

                _installed_integrations.add(identifier)

    for identifier in integrations:
        logger.debug("Enabling integration %s", identifier)

    return integrations


class DidNotEnable(Exception):
   """ The integration could not be enabled due to a trivial user error like `flask` not being installed for the `FlaskIntegration`. This exception is silently swallowed for default integrations, but reraised for explicitly enabled integrations.
   """

class Integration(object):
   """Baseclass for all integrations.
   
   To accept options for an integration, implement your own constructor that saves those options on `self`.
   """

   # String unique ID of integration type
   identifier: str = None

   @staticmethod
   def setup_once():
      # type: () -> None
      """Initialize the integration.
      
      This function is only called once, ever. Configuration is not available at this point, so the only thing to do here is to hook into exception handlers, and perhaps do monkeypatches.
      
      Inside those hooks `Integration.current` can be used to access the instance again.
      """
      raise NotImplementedError()
