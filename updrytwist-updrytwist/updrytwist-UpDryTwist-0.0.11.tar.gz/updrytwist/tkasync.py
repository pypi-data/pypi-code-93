import asyncio

from updrytwist import config
import threading
import tkinter
import logging

DEFAULT_QUEUE_CHECK_MSEC = 250
DEFAULT_DEBUG_ASYNCIO = False
DEFAULT_SLEEP_SECONDS = 1

_LOGGER = logging.getLogger(__name__)


class ThreadedGuiHook:

    def __init__ ( self, configuration : config.Config ):

        threadedConfig = configuration.value("ThreadedGui")
        self.queueCheckMsec   = config.dictread( threadedConfig, "QueueCheckMsec", DEFAULT_QUEUE_CHECK_MSEC )
        self.debugAsyncio     = config.dictread( threadedConfig, "DebugAsyncio",   DEFAULT_DEBUG_ASYNCIO )
        self.sleepSeconds     = config.dictread( threadedConfig, "SleepSecondsEachLoop", DEFAULT_SLEEP_SECONDS )
        self.master       = None
        self.threadClient = None
        self.keepLooping  = True
        self.tasks        = []

    def queueCheckEveryNMsec ( self ):
        return self.queueCheckMsec

    def initAsync ( self ):
        pass

    def addTask ( self, task ) -> None:
        self.tasks.append( task )

    def createTasks ( self ):
        # Create the tasks that will be used for the different async loop(s)
        pass

    def acceptTick ( self ):
        pass

    async def defaultAsyncLoop ( self ):
        self.createTasks()

        while self.keepLooping:
            try:
                await asyncio.sleep(self.sleepSeconds)
            except asyncio.CancelledError:
                self.keepLooping = False
            except Exception as e:
                _LOGGER.error( f'Unanticipated error in defaultAsyncLoop: {e}')

    def quitAsyncLoop ( self ):
        self.keepLooping = False
        self.threadClient.endApplication()

    def runAsyncLoop ( self ):
        asyncio.run( self.defaultAsyncLoop(), debug=self.debugAsyncio )

    def processQuitAsyncLoop ( self ):
        self.keepLooping = False
        for task in self.tasks:
            task.cancel()


class ThreadedClient:
    """
    Launch the main part of the GUI and the worker thread. periodicCall and
    endApplication could reside in the GUI part, but putting them here
    means that you have all the thread controls in a single place.
    """
    def __init__( self, master, hook : ThreadedGuiHook ):
        """
        Start the GUI and the asynchronous threads. We are in the main
        (original) thread of the application, which will later be used by
        the GUI as well. We spawn a new thread for the worker (I/O).
        """
        self.master = master
        self.hook   = hook

        hook.master       = master
        hook.threadClient = self

        self.hook.initAsync()

        # Set up the thread to do asynchronous I/O
        # More threads can also be created and used, if necessary
        self.running = 1
        self.thread1 = threading.Thread(target=self.workerThread1)
        self.thread1.start()

        # Start the periodic call in the GUI to check if the queue contains
        # anything
        self.periodicCall()

    def periodicCall(self):
        """
        Check every n-many ms if there is something new in the queue.
        """
        try:

            self.hook.acceptTick()
            if not self.running:
                # This is the brutal stop of the system. You may want to do
                # some cleanup before actually shutting it down.
                import sys
                sys.exit(1)
        except asyncio.CancelledError:
            self.endApplication()
            return
        except Exception as e:
            _LOGGER.info( f'Exception in ThreadedClient.periodicCall: {e}')

        self.master.after(self.hook.queueCheckEveryNMsec(), self.periodicCall)

    def workerThread1(self):
        """
        This is where we handle the asynchronous I/O. For example, it may be
        a 'select(  )'. One important thing to remember is that the thread has
        to yield control pretty regularly, by select or otherwise.
        """
        self.hook.runAsyncLoop()

    def endApplication(self):
        self.running = 0
        self.hook.processQuitAsyncLoop()

    @staticmethod
    def runLoop ( hook : ThreadedGuiHook ) -> None:
        root = tkinter.Tk()
        client = ThreadedClient( root, hook )
        root.mainloop()
