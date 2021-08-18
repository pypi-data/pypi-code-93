# PySide2
from PySide2 import QtCore


class _GenericRunnableSignals(QtCore.QObject):
    """
    QObject with custom signals.

    This is used in AlgorandWorker to signal a success with return value or an error.
    """
    success = QtCore.Signal(object)
    error = QtCore.Signal(Exception)


class GenericRunnable(QtCore.QRunnable):
    """
    This class is used to run a callable in a thread using QThreadPool.

    We use this instead of a separate class for every piece of code we could ever need to run.
    As long as it's a simple blocking call with a return value this is fine. Just connect to result signal with the
    function that process the return value.
    """
    def __init__(self, fn: callable, *args, **kwargs):
        super().__init__()

        self._fn = fn
        self._args = args
        self._kwargs = kwargs
        self.signals = _GenericRunnableSignals()

    def run(self):
        """
        This overridden method calls a callable fn with args, kwargs parameters.

        This method gets called once this object is inside a QThreadPool.
        """
        try:
            result = self._fn(*self._args, **self._kwargs)
        except Exception as e:
            self.signals.error.emit(e)
        else:
            self.signals.success.emit(result)


def start_worker(
        pool: QtCore.QThreadPool,
        fn: callable,
        fn_success: callable = None,
        fn_error: callable = None) -> GenericRunnable:
    runnable = GenericRunnable(fn)
    runnable.signals.success.connect(fn_success)
    runnable.signals.error.connect(fn_error)

    pool.start(runnable)

    return runnable


# This thread pool will be used to issue blocking calls of algosdk.
# If we want to setup a timeout timer for an algosdk blocking call, a technique could be to start thread A
#  that starts a timer.
#  Then thread A starts a thread B with the algosdk blocking call. Then only two things can happen:
#   1. thread B responds to thread A within the timer timeout
#   2. thread B does not respond to thread A within the timer timeout
#  Either way we get an answer from thread A within some fixed time.
