
import collections
import logging
import multiprocessing as mp
import os
import queue
import random
import traceback

# import torch
import tqdm

# from textattack.attack_results import (
#     FailedAttackResult,
#     MaximizedAttackResult,
#     SkippedAttackResult,
#     SuccessfulAttackResult,
# )
# from textattack.shared.utils import logger

from .attack import Attack
from .attack_args import AttackArgs

class Attacker:

    def __init__(self, attack, dataset, attack_args=None):
        assert isinstance(
            attack, Attack
        ), f"`attack` argument must be of type `textattack.Attack`, but got type of `{type(attack)}`."
        assert isinstance(
            dataset, textattack.datasets.Dataset
        ), f"`dataset` must be of type `textattack.datasets.Dataset`, but got type `{type(dataset)}`."

        if attack_args:
            assert isinstance(
                attack_args, AttackArgs
            ), f"`attack_args` must be of type `textattack.AttackArgs`, but got type `{type(attack_args)}`."
        else:
            attack_args = AttackArgs()

        self.attack = attack
        self.dataset = dataset
        self.attack_args = attack_args
        self.attack_log_manager = None

        # This is to be set if loading from a checkpoint
        self._checkpoint = None