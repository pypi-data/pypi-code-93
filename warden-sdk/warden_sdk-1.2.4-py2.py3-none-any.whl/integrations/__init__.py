"""Central setup of integrations.

This module will load all of the integrations necessary for the initialized `warden_sdk`. Default integrations will always be loaded and supplementary integrations must be called when initializing the sdk.

  Typical usage example:

  from warden_sdk.integrations import setup_integrations
  setup_integrations(self.options["integrations"])
"""
from __future__ import absolute_import

from warden_sdk.utils import iteritems, logger
from typing import (Tuple)

_installed_integrations = set()

def _generate_default_integrations_iterator(integrations):
   """Generate list of Integrations.

   This function creates a list of imported integrations that are required, mainly the default integrations.

   Args:
      integrations: A list of integrations as functions.

   Returns:
      A list of integrations that have been imported, now ready to be setup.
   """
   def default_integrations():
      from importlib import import_module

      all_import_strings = integrations

      for import_string in all_import_strings:
         try:
            module, cls = import_string.rsplit(".", 1)
            yield getattr(import_module(module), cls)
         except SyntaxError as e:
            logger.debug(
                f"Did not import default integration {import_string}: {e}"
            )

   if isinstance(default_integrations.__doc__, str):
      for import_string in integrations:
         default_integrations.__doc__ += "\n- `{}`".format(import_string)

   return default_integrations


default_integrations = _generate_default_integrations_iterator(integrations=(
    "warden_sdk.integrations.flask.FlaskIntegration",
    "warden_sdk.integrations.logging.LoggingIntegration",
    "warden_sdk.integrations.excepthook.ExcepthookIntegration",
    "warden_sdk.integrations.awslambda.AwsLambdaIntegration",
))
del _generate_default_integrations_iterator


def setup_integrations(integrations: Tuple[list, str], with_defaults=True, flask=True):
   """Initialize integrations required for `warden_sdk` to work.

   This function will iterate through the integrations generated from the `_generate_default_integrations_iterator()` and run each integrations' `setup_once()` function.

   Args:
      integrations: A tuple of list and str containing the requested, supplementary integrations from the `self.options['integrations']` in the `client`.

      with_defaults: A boolean to check if we need defaults.
   
   Returns:
      A list of integrations that were setup.
   """
   integrations: dict = dict(
       (integration.identifier, integration)
       for integration in integrations or ()
   )

   if with_defaults:
      for integration_cls in default_integrations():
         if integration_cls.identifier not in integrations:
            instance = integration_cls()
            integrations[instance.identifier] = instance

   for identifier, integration in iteritems(integrations):
      if identifier not in _installed_integrations:
         # if identifier == 'flask' and not flask:
         #    continue

         type(integration).setup_once()
         _installed_integrations.add(identifier)

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
