from enum import Enum


class ProviderVendor(Enum):
    IBMQ = "IBMQ"
    AZURE_QUANTUM = "Azure Quantum"
    AWS_BRAKET = "AWS Braket"


class BackendNames(Enum):
    AWS_BRAKET_SV1 = "SV1"
    AWS_BRAKET_TN1 = "TN1"
    AWS_BRAKET_DM1 = "dm1"
    AWS_BRAKET_ASPEN_9 = "Aspen-9"
    AWS_BRAKET_IONQ = "IonQ Device"
    IBMQ_AER_SIMULATOR = "aer_simulator"
    IBMQ_AER_SIMULATOR_STATEVECTOR = "aer_simulator_statevector"
    IBMQ_AER_SIMULATOR_DENSITY_MATRIX = "aer_simulator_density_matrix"
    IBMQ_AER_SIMULATOR_MATRIX_PRODUCT_STATE = "aer_simulator_matrix_product_state"
    AZURE_QUANTUM_IONQ = "IonQ"
    AZURE_QUANTUM_HONEYWELL = "Honeywell"


BACKEND_PROVIDERS_DICT = {
    ProviderVendor.AWS_BRAKET: [
        BackendNames.AWS_BRAKET_SV1,
        BackendNames.AWS_BRAKET_TN1,
        BackendNames.AWS_BRAKET_DM1,
        BackendNames.AWS_BRAKET_ASPEN_9,
        BackendNames.AWS_BRAKET_IONQ,
    ],
    ProviderVendor.IBMQ: [
        BackendNames.IBMQ_AER_SIMULATOR,
        BackendNames.IBMQ_AER_SIMULATOR_STATEVECTOR,
        BackendNames.IBMQ_AER_SIMULATOR_DENSITY_MATRIX,
        BackendNames.IBMQ_AER_SIMULATOR_MATRIX_PRODUCT_STATE,
    ],
    ProviderVendor.AZURE_QUANTUM: [
        BackendNames.AZURE_QUANTUM_IONQ,
        BackendNames.AZURE_QUANTUM_HONEYWELL,
    ],
}
