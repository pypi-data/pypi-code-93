import threading
import time
from .jobcontext import JobContext


class Worker(threading.Thread):
    def __init__(self, resource, channel, logger, context:JobContext):
        super().__init__()
        self.daemon = True
        self.resource = resource
        self.channel = channel
        self.logger = logger
        self.context = context

    def run(self):
        r = self.resource(channel=self.channel,
                          logger=self.logger,
                          context=self.context)

        # joblog start message
        tm_st = int(time.time())
        self.channel.publish_notify(self.context, 'job start', 1)
        self.logger.info("%s, start app.", self.context.action_app)

        """user main function invoke
        return value
            success = 0
            failure = 1
        """
        rt = r.main()
        if rt == 0:
            tm_ed = int(time.time())
            self.logger.info("%s, end app ok", self.context.action_app)
            self.channel.publish_job(self.context)
            self.channel.publish_notify(self.context, 'job end, success', 3, tm_ed-tm_st)
        else:
            self.logger.info("%s, end app failed", self.context.action_app)
            self.channel.publish_notify(self.context, 'job end, failed', 3)
