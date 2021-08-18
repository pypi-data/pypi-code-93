#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Cédric Dumay <cedric.dumay@gmail.com>


"""
import os

from cdumay_result import Result
from kser.python_kafka.producer import Producer
from kser_crypto.schemas import CryptoSchema


class CryptoProducer(Producer):
    # noinspection PyUnusedLocal
    def _send(self, topic, kmsg, timeout=60):
        result = Result(uuid=kmsg.uuid)
        try:
            self.client.send(topic, CryptoSchema(context=dict(
                secretbox_key=os.getenv("KSER_SECRETBOX_KEY", None)
            )).encode(self._onmessage(kmsg)).encode("UTF-8"))

            result.stdout = "Message {}[{}] sent in {}".format(
                kmsg.entrypoint, kmsg.uuid, topic
            )
            self.client.flush()

        except Exception as exc:
            result = Result.from_exception(exc, kmsg.uuid)

        finally:
            if result.retcode < 300:
                return self._onsuccess(kmsg=kmsg, result=result)
            else:
                return self._onerror(kmsg=kmsg, result=result)
