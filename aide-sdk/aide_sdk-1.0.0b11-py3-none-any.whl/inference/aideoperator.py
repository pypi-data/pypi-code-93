import abc

from aide_sdk.model.operatorcontext import OperatorContext


class AideOperator(abc.ABC):

    @abc.abstractmethod
    def process(self, context: OperatorContext) -> OperatorContext:
        """`process` must be implemented in the Operator. This is where
        the operator's work is carried out.

        :param context: An OperatorContext object containing a list of available resources.
                        This object allows accessing and saving resources.
        :return: The same OperatorContext object after adding new resources.
        """
        raise NotImplementedError
