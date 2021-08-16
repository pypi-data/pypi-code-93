import logging
from caterpillar_common.common.log import Log
Log("demo_log")
log=logging.getLogger("demo_log")


class TestLog(object):
    def test_log_1(self):
        log.info("hello info ...")
        log.error("hello error ... ")