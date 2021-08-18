
class PyAssemblyPaymentsException(Exception):
    pass


class PyAssemblyPaymentsNotImplementedException(PyAssemblyPaymentsException):
    pass


class PyAssemblyPaymentsBadRequest(PyAssemblyPaymentsException):
    pass


class PyAssemblyPaymentsForbidden(PyAssemblyPaymentsException):
    pass


class PyAssemblyPaymentsNotFound(PyAssemblyPaymentsException):
    pass


class PyAssemblyPaymentsConflict(PyAssemblyPaymentsException):
    pass


class PyAssemblyPaymentsUnprocessableEntity(PyAssemblyPaymentsException):
    pass