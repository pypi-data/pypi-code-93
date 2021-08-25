import logging
import argparse
from abc import ABC, abstractmethod

"""
Core (abstract) Processing module for data access across a network

Defines the following methods:
    _defineArgs() (abstract): allows the overriding class to define a custom list of appropriate arguments for the data 
        request
    run(): Assumes a call is made from console which will utilize the _defineArgs function to define the relevant args
        for the data call in conjunction with argparse to determine the parameters provided by the user. Arguments are 
        then passed to the main function which maintains the logic to actually perform the data request
    main(): Validates the input arguments and passes them to the requestData() function.
    requestData() (abstract):  Allows the overriding class to define a specific method to call for data. This could be 
        sql, graphql, webrequest, etc. Expected to return a data set in an undefined form. 
    _validateArgs(): Anticipated to be used by the inherited class within the main function to validate that the args
        that are provided are appropriate per the definition in the _defineArgs() method
"""




class DataAccessExecutor(ABC):
    def __init__(self, label, loggingLvl = None):
        self.label = label
        self.requestArgs = {}
        self.loggingLvl = loggingLvl

    @abstractmethod
    def _defineInputArgs(self):
        pass

    def run(self):
        # Gather Arguments
        parser = argparse.ArgumentParser(description=self.label)
        arg_defs = self._defineInputArgs()

        for arg in arg_defs:
            if arg.get('required', False) == True:
                parser.add_argument('-' + str(arg['short']), '--' + str(arg['long']),
                                type=arg['type'],
                                help=arg['help'],
                                required=True)
            else:
                parser.add_argument('-' + str(arg['short']), '--' + str(arg['long']),
                                    default=arg['default'],
                                    type=arg['type'],
                                    help=arg['help'])

        args = parser.parse_args()
        return self.main(vars(args), context="CONSOLE")

    def main(self, inargs, context=None, **kwargs):
        if context is None:
            context = self.label

        validInputArgs = self._validateInputArgs(inargs, context)
        requestArgs = self._defineRequestArgs()

        return self.request(validInputArgs, requestArgs, context, **kwargs)

    @abstractmethod
    def request(self, inputargs, requestargs, context, **kwargs):
        pass

    @abstractmethod
    def _defineRequestArgs(self):
        pass

    def _validateInputArgs(self, inargs, context=None):
        inargs = inargs if inargs else {}
        logging.log(self.loggingLvl, f"[{context}]: Input Args for [{self.label}]: {inargs}")

        args = self._defineInputArgs()
        ret = {}
        for arg in args:
            """
            New dictionary will have data in the form: 
             {   key == the parameter name defined in the calling class
                 value == value provided by the user, method or default if not a required param}
            """
            if arg.get('required', False) == False:
                ret[arg['long']] = inargs.get(arg['long'], arg['default'])
            else:
                if arg['long'] in inargs:
                    ret[arg['long']] = inargs[arg['long']]
                else:
                    raise Exception(f"value {arg['long']} was not provided")

        logging.log(self.loggingLvl, f"[{context}]: Validated Args for [{self.label}]: {ret}")

        return ret

