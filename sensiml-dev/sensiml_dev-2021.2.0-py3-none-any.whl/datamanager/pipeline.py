from warnings import warn


class PipelineWarning(Warning):
    """Base class for a pipeline warning"""

    pass


class PipelineError(Exception):
    """Base class for a pipeline error"""

    pass


class PipelineStep(object):
    """Base class for a pipeline step"""

    def __init__(self, name, step_type="default"):
        self._inputs = []
        self._outputs = []
        self._name = name
        self._step_type = step_type
        self._feature_table = None

    @property
    def feature_table(self):
        return self._feature_table

    @feature_table.setter
    def feature_table(self, value):
        self._feature_table = value

    @property
    def inputs(self):
        return self._inputs

    @property
    def outputs(self):
        return self._outputs

    @outputs.setter
    def outputs(self, outputs):
        self._outputs = outputs

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def step_type(self):
        return self._step_type

    def _check_inputs(self, output_vars=()):
        """Compares the list of inputs with the given output_vars list.

        Args:
            output_vars (list[str]): strings representing the current set of output variables

        Returns:
            (list): unmatched inputs, or an empty list if all inputs are matched
        """
        unmatched_inputs = []
        for input in self.inputs:
            if not input in output_vars:
                unmatched_inputs.append(input)
        return unmatched_inputs

    def _check_outputs(self, output_vars=(), is_last=False):
        """Compares the outputs from the item with the other output_vars from the pipeline.

        Args:
            output_vars (list[str]): strings representing the current set of output variables
            is_last (bool): True if item is the last step, otherwise False (default)

        Returns:
            (list): duplicate outputs, or an empty list if all outputs are unique

        Raises:
            PipelineError if step is not the last one and does not have any outputs
            PipelineWarning if step is the last one and does not have any outputs
        """
        duplicate_outputs = []
        if self.outputs:
            for output in self.outputs:
                if output in output_vars:
                    duplicate_outputs.append(output)
        elif is_last:
            warn(
                "{0} {1} does not have any outputs.".format(
                    self._step_type, self._name
                ),
                PipelineWarning,
            )
        else:  # is_last = False
            raise PipelineError(
                "{0} {1} does not have any outputs.".format(self._step_type, self._name)
            )
        return duplicate_outputs
