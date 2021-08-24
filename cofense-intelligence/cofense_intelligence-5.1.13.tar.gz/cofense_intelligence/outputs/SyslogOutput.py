from cofense_intelligence.output import CofenseIntegration
from cofense_intelligence.syslog import Syslog


class SyslogOutput(CofenseIntegration):
    def __init__(self, config, **kwargs):
        super(SyslogOutput, self).__init__(config, **kwargs)
        self.syslog = Syslog(host=self.args.syslog_host,
                             port=self.args.syslog_port,
                             level=self.args.syslog_level,
                             facility=self.args.syslog_facility,
                             protocol=self.args.syslog_protocol)

    def process(self, mrti):
        self.syslog.send(mrti)
