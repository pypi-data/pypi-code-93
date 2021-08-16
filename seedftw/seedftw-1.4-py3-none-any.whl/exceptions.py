class MissingApiKeyError(Exception):
    """Raised when an API key has not been loaded.

    Attributes:
        message -- explanation of why the specific transition is not allowed
        environment_variable -- enviroment variable that should contain the key
    """

    def __init__(self, message, environment_variable, create_at_url):
        print(
            "You are missing an API loaded in the environment variable "
            + environment_variable
            + ".\nIf you do not have one, create one on: "
            + create_at_url
            + "\n\n"
        )
        self.message = message
        self.environment_variable = environment_variable
        self.create_at_url = create_at_url


class MovedToPlotneat(Exception):
    def __init__(self):
        super().__init__(
            """
        This code was moved to plotneat, which can be downloaded here:
        https://gitlab.com/Pierre_VF/plotneat
        """
        )


class MovedToSenasopt(Exception):
    def __init__(self, new_function):
        super().__init__(
            """This function is deprecated and has been removed.

            To access a similar functionality, refer to the package "senasopt" on PyPi.

            The corresponding function in the package is: senasopt.{}
            (you might however have to do slight aaptation of your code at the interface)

            """.format(
                new_function
            )
        )
