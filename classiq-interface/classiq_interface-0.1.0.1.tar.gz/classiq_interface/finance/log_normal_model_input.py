import numpy as np
import pydantic


class LogNormalModelInput(pydantic.BaseModel):
    num_qubits: pydantic.PositiveInt = pydantic.Field(
        description="Number of qubits to represent the probability."
    )
    mu: pydantic.confloat(ge=0) = pydantic.Field(
        description="Mean of the Normal distribution variable X s.t. ln(X) ~ log-normal."
    )
    sigma: pydantic.confloat(gt=0) = pydantic.Field(
        description="Std of the Normal distribution variable X s.t. ln(X) ~ log-normal."
    )

    @property
    def bounds(self):
        mean = np.exp(self.mu + self.sigma ** 2 / 2)
        variance = (np.exp(self.sigma ** 2) - 1) * np.exp(2 * self.mu + self.sigma ** 2)
        stddev = np.sqrt(variance)
        low = np.maximum(0, mean - 3 * stddev)
        high = mean + 3 * stddev
        return low, high

    @property
    def num_model_qubits(self):
        return self.num_qubits
