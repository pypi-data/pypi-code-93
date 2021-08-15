from dataclasses import dataclass
from pollination_dsl.function import Function, command, Inputs, Outputs


@dataclass
class MatrixMultiplication(Function):
    """Multiply a matrix with conversation numbers."""
    conversion = Inputs.str(
        description='conversion as a string which will be passed to -c',
        default='47.4 119.9 11.6'
    )

    input_matrix = Inputs.file(
        description='Path to input matrix.', path='input.ill'
    )

    output_format = Inputs.str(default='-fa')

    @command
    def create_matrix(self):
        return 'rmtxop {{self.output_format}} input.ill -c {{self.conversion}} | ' \
            'getinfo - > output.ill'

    output_matrix = Outputs.file(description='New matrix file.', path='output.ill')
