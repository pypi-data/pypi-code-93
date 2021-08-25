from io import StringIO
from gawseed.threatfeed.events.reporter import EventStreamReporter

class RedmineReporter(EventStreamReporter):
    """Takes a markdown output and sends the results to a redmine
    instance."""

    def __init__(self, conf):
        super().__init__(conf)

        self.require(["redmine_host"])
        self._redmine_host = self.config("redmine_host",
                                         help="Redmine host to connect to")

    def new_output(self, count, **kwargs):
        self._stream = StringIO()
        

    def maybe_close_output(self):
        pass # send to redmine here
    
