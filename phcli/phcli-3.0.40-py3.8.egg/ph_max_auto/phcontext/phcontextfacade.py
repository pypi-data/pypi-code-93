# -*- coding: utf-8 -*-
"""alfredyang@pharbers.com.

This module document the usage of class pharbers command context,
"""
import base64

from phcli.ph_aws.ph_s3 import PhS3
from phcli.ph_aws.ph_sts import PhSts
from phcli.ph_max_auto import define_value as dv
from phcli.ph_max_auto.phcontext.ph_ide.ph_ide_c9 import PhIDEC9
from phcli.ph_max_auto.phcontext.ph_ide.ph_ide_jupyter import PhIDEJupyter
from phcli.ph_logs.phLogs.ph_logs import phs3logger, LOG_DEBUG_LEVEL, LOG_INFO_LEVEL, LOG_WARN_LEVEL, LOG_ERROR_LEVEL


class PhContextFacade(object):
    def __init__(self, **kwargs):
        log_level = kwargs.pop('log_level')
        if log_level == 'info':
            log_level = LOG_INFO_LEVEL
        elif log_level == 'warn':
            log_level = LOG_WARN_LEVEL
        elif log_level == 'error':
            log_level = LOG_ERROR_LEVEL
        else:
            log_level = LOG_DEBUG_LEVEL

        self.logger = phs3logger(level=kwargs.get("log_level", log_level))
        self.phsts = PhSts().assume_role(
            base64.b64decode(dv.ASSUME_ROLE_ARN).decode(),
            dv.ASSUME_ROLE_EXTERNAL_ID,
        )
        self.phs3 = PhS3(phsts=self.phsts)
        self.__dict__.update(kwargs)
        self.ide_table = {
            'c9': PhIDEC9,
            'jupyter': PhIDEJupyter,
        }
        self.ide_inst = self.ide_table[self.ide](**self.__dict__)

    def command_create_exec(self):
        self.logger.debug("sub command create")
        self.ide_inst.create()

    def command_complete_exec(self):
        self.logger.debug("sub command complete")
        self.ide_inst.complete()

    def command_run_exec(self):
        self.logger.debug("sub command run")
        self.ide_inst.run()

    def command_combine_exec(self):
        self.logger.debug("sub command combine")
        self.ide_inst.combine()

    def command_dag_exec(self):
        self.logger.debug("sub command dag")
        self.ide_inst.dag()

    def command_publish_exec(self):
        self.logger.debug("sub command publish")
        self.ide_inst.publish()

    def command_recall_exec(self):
        self.logger.debug("sub command recall")
        self.ide_inst.recall()

    def command_online_run_exec(self):
        self.logger.debug("sub command online_run")
        self.ide_inst.online_run()

    def command_status_exec(self):
        self.logger.debug("sub command status")
        self.ide_inst.status()
