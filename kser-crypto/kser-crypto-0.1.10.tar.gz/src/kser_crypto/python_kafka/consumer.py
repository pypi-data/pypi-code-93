#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. codeauthor:: Cédric Dumay <cedric.dumay@gmail.com>


"""
from kser.python_kafka.consumer import Consumer
from kser_crypto.controller import CryptoController


class CryptoConsumer(Consumer):
    REGISTRY = CryptoController
