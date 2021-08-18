"""Classes and functions related to expectation development
Playground is a class to develop your expectations. For each expectation_type it has a method.
If you run this method it runs the expectation on the given dataframe and returns this expectation definition.
Playground class doesn't exist anymore, objects are constructed on the fly
from the passed class with custom expectaitons, plus expressions.
"""
from typing import Union

from .expectation_attributes.expectation import Expectation


def run_expectation(
    self,
    expectation: Union[dict, Expectation, 'ExpectationConfiguration', 'ExpectationValidationResult']
) -> 'ExpectationValidationResult':
    """Run the given expectation for development or debugging."""
    # get the expectation from whatever came
    expectation = Expectation(expectation=expectation)
    # run the expectaiton
    exp_method = getattr(self, expectation.expectation_type)
    return exp_method(**expectation.kwargs)
