from abc import ABC, abstractmethod
from mitosheet.state import State
from typing import Dict, List
 
class StepPerformer(ABC, object):
    """
    The abstract base class for a step generator, which are the set
    of classes that execute, transpile, and describe steps. 
    """

    @classmethod
    @abstractmethod
    def step_version(cls) -> int:
        """
        Returns the version of the step. Changes when the parameters
        of the step change.
        """
        pass

    @classmethod
    @abstractmethod
    def step_type(cls) -> str:
        """
        The name of the step used internally. If you change this, you must upgrade
        the step and bump the version.
        """
        pass

    @classmethod
    @abstractmethod
    def step_display_name(cls) -> str:
        """
        The name of the step that is displayed to the user
        in the frontend.
        """
        pass
    
    @classmethod
    @abstractmethod
    def step_event_type(cls) -> str:
        """
        The type of the edit event that generates this type of step.
        """
        pass

    @classmethod
    def saturate(cls, prev_state: State, params) -> Dict[str, str]:
        """
        Given the parameters of the step, will saturate the event with
        more parameters based on the passed prev_state. 
        """
        # By default, we don't do anything with the saturate
        return params

    @classmethod
    @abstractmethod
    def execute(cls, prev_state: State, **params) -> State:
        """
        Execute always returns the post_state, and optionally returns a dictionary
        of execution_data, which is data that may be useful to the transpiler in
        transpiling the code.
        """
        pass

    @classmethod
    @abstractmethod
    def transpile(cls, prev_state: State, post_state: State, **params) -> List[str]:
        """
        Returns a list of the Python code lines that corresponds to this 
        step being executed.
        """
        pass

    @classmethod
    @abstractmethod
    def describe(cls, **params) -> str:
        """
        Describes the step in a single sentence, usually for comments or for presentation
        to the user in the frontend.
        """
        pass