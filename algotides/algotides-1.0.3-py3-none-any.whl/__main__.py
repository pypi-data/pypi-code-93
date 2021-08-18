"""
This main function will initialize PySide2 & Main and manage the starting of the program.
"""

# Python
import sys
import asyncio

# PySide2
from PySide2 import QtWidgets
# qasync
import qasync


# TODO: We could use an abstract class that forces the implementation of self.restart()
# TODO Maybe look into Qt model/view because management of contacts, wallets and addresses is getting out of hand
#   especially in TransactionWindow.
# In this application we make many calls to algosdk asynchronously using aioify module. These calls are supposed to
#   happen in a separate thread and when they are done the execution continues from the awaited instruction.
#   while the thread is spinning we don't block main thread event loop.
# However we also make calls to exec_() through aioify. This should mean that every window called through aioify is
#   spinning in its own thread. This could come back to bite us.
# For the final plot twist: https://doc.qt.io/qt-5/qapplication.html#exec
#   "... As a special case, modal widgets like QMessageBox can be used before calling exec(),
#   because modal widgets call exec() to start a local event loop."
# With emphasis on the last sentence we assume that, as long as the window we are exec_()-ing is modal, we are
#   completely fine if we spin it in a separate thread.
# As
#   https://stackoverflow.com/questions/33605186/does-calling-qdialogexec-in-a-slot-block-the-main-event-loop/33606782#33606782
#   points out every call to a slot in the main event loop while it's blocked can be a source of nasty bugs.
# It would be a better solution altogether if we could keep all the Qt stuff on the main thread and
#   all the await elsewhere.
# Another interesting question is: what happens in the separated used to exec_()? Does it spin up a Qt Event Loop or a
#   qasync event loop?

# Evidence shows that once you call exec_() through qasync it can indeed spawn in another thread.
# It is also true that in the spawned thread we have a qasync QSelectorEventLoop as the default event loop.
#   And the id() of that QSelectorEventLoop is the same as the one in the main thread. Strange indeed.
def main():
    # Manager of all things regarding a widget-based Qt5 app.
    #  Eg.: mainloop, events, initialization, finalization, ...
    app = QtWidgets.QApplication([])

    # qasync is the bridge between python asyncio and PySide2 event loop.
    #   It allows us to use asyncio without interfering with PySide2 runtime environment.
    event_loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(event_loop)

    # This import has to be done here because there are several static resources inside this package which
    #  will be loaded during the import of the package itself. So because most misc are PySide2 objects
    #  QApplication needs to be running to perform all task needed.
    from algotides.interfaces.main.window import MainWindow

    MainWindow.initialize()

    main_window = MainWindow()
    main_window.show()

    with event_loop:
        event_loop.run_forever()


if __name__ == '__main__':
    sys.exit(main())
