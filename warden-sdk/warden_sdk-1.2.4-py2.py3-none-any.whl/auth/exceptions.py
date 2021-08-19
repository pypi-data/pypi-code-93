"""Contains all custom exceptions.
"""


class JWT(object):

   class InvalidToken(Exception):
      """Exception raised for errors in the input salary.

      Attributes::
         message (str): explanation of the error
      """

      def __init__(self, message="Invalid token."):
         self.message = message
         super().__init__(self.message)
