"""A collection of filters to use with feyn Models."""

from typing import List, Union
import feyn

from feyn._qlnew import _spec_to_fname

class Complexity:
    """Use this class to get a filter for selecting models with a specific complexity."""

    def __init__(self, complexity: int):
        self.complexity = int(complexity)

    def __call__(self, model: feyn.Model) -> bool:
        return model.edge_count == self.complexity


class ContainsInputs:
    """Use this class to get a filter for including only models that contain specific named inputs."""

    def __init__(self, input_name: Union[str, List[str]]):
        self.names = input_name

    def __call__(self, model: feyn.Model) -> bool:
        if isinstance(self.names, str):
            return self.names in model
        return all(name in model for name in self.names)


class ExcludeFunctions:
    """Use this class to get a filter for excluding models that contain any of the named functions."""

    def __init__(self, functions: Union[str, List[str]]):
        if isinstance(functions, str):
            functions = [functions]
        self.functions = functions

    def __call__(self, model: feyn.Model) -> bool:
        for node in model:
            if node.spec.startswith("cell:") and any(
                fname in node.spec for fname in self.functions
            ):
                return False
        return True


class ContainsFunctions:
    """Use this class to get a filter for including only models that exclusively consist of the named functions."""

    def __init__(self, functions: Union[str, List[str]]):
        if isinstance(functions, str):
            functions = [functions]
        self.functions = set(functions)

    def __call__(self, model: feyn.Model) -> bool:
        model_functions = set(
            _spec_to_fname(node.spec) for node in model if node.spec.startswith("cell:")
        )
        return self.functions == model_functions
