from abc import ABC, abstractmethod
from typing import NoReturn, Dict

from fathom_lib.pipeline_runner import PipelineRunner


class Runnable(ABC):
    """
    The idea behind this class:
    Runnable is a workflow component that uses the model and can be run (e.g. saving model or
    validation). Note that by ``run`` signature this method accepts only ``model`` parameter.
    Other parameters should be supplied in init method. This separation is because of our idea
    that the model will be plugged in from other components, whereas the other parameters required
    for ``run`` to execute will be supplied by user in the UI. This is exactly how it is done e.g.
    with sklearn estimators, where all hyperparameters are specified by the user in UI,
    and the parameters of fit/predict methods come from other sockets.

    Also note that although ``run`` returns nothing, other methods can be created to return some
    objects that could be used by other components. Those methods would work as outgoing sockets
    just like transform or predict methods in sklearn objects.
    """

    @abstractmethod
    def run(self, model: PipelineRunner, context: Dict) -> NoReturn:
        pass


class SaveModel(Runnable):
    """
    Just saves the model.

    Parameters
    ----------
    path: str
        path to which the model should be saved
    """

    def __init__(self, path: str):
        self._path = path

    def run(self, model: PipelineRunner, context: Dict) -> NoReturn:
        model.save(self._path)
