"""User class to maintain state and user information.

The User module allows us to collect all of the relevant information for a user and allow the system to access the relevant information about a User that necessary to propagate internally for clear understanding of what's going on with the system.
"""
import sys

from warden_sdk.hub import Hub
from warden_sdk.utils import (get_options, logger)
# from warden_sdk.integrations.flask import FlaskIntegration
from warden_sdk.integrations.awslambda import AwsLambdaIntegration

from typing import (Any, Optional)


class _User(object):
   """User class contains all information about the requester.
   """
   fid: Optional[str] = None
   __scope: Optional[list] = None

   def __init__(self) -> None:
      pass

   def setup(self, request: Any) -> None:
      hub = Hub.current
      client = hub.client
      options = get_options(client.options)

      # flask_integration = hub.get_integration(FlaskIntegration)
      aws_integration = hub.get_integration(AwsLambdaIntegration)

      if options['debug'] and options['user_fid'] is None or options[
          'user_scope'] is None:
         return

      # TODO(MP): ugly and complex section. Need to fix-up how we can debug
      #  the API without having to turn it off... Can we simulate another
      #  User? Should be included in the `options`... Let's try.
      __context = None
      if options['debug']:
         logger.info(
             f"Setting up proto-user for debugging: {options['user_fid']}")
         self.fid = options['user_fid']
         self.scope = options['user_scope']
      else:
         if aws_integration:
            __context = request.environ['serverless.event']['requestContext'][
                'authorizer']

            self.fid = __context['fid']
            self.scope = __context['scope']
         else:
            self.fid = options['user_fid']
            self.scope = options['user_scope']

      if options['scopes'] is None:
         raise ValueError('Missing scopes.')

      self.verify_scopes(options['scopes'])

   @property
   def scope(self) -> list:
      return self.__scope

   @scope.setter
   def scope(self, scope):
      self.__scope = scope.split(' ')

   def verify_scopes(self, scopes) -> bool:
      if not any(scope in self.scope for scope in scopes):
         raise Exception({
             'error': 'invalid_request',
             'error_description': 'Invalid scopes.'
         })

      return True


User = (lambda: _User)()

# def __check_enviorn() -> bool:
#    if "bootstrap" in sys.modules:
#       return True
#    elif "__main__" in sys.modules:
#       if hasattr(sys.modules["__main__"], "bootstrap"):
#          # awslambdaric python module in container builds
#          return True
#       return True

#    return False
