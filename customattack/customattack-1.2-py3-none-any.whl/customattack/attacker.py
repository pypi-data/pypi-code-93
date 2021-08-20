
import collections
import logging
import multiprocessing as mp
import os
import queue
import random
import traceback
import tqdm
import customattack

import torch
# from customattack.attack_results import (
#     FailedAttackResult,
#     MaximizedAttackResult,
#     SkippedAttackResult,
#     SuccessfulAttackResult,
# )
from customattack.shared.utils import logger
from .attack import Attack
from .attack_args import AttackArgs

class Attacker:
    def __init__(self, attack, dataset, attack_args=None):
        assert isinstance(
            attack, Attack
        ), f"`attack` argument must be of type `customattack.Attack`, but got type of `{type(attack)}`."
        assert isinstance(
            dataset, customattack.datasets.Dataset
        ), f"`dataset` must be of type `customattack.datasets.Dataset`, but got type `{type(dataset)}`."

        if attack_args:
            assert isinstance(
                attack_args, AttackArgs
            ), f"`attack_args` must be of type `customattack.AttackArgs`, but got type `{type(attack_args)}`."
        else:
            attack_args = AttackArgs()

        self.attack = attack
        self.dataset = dataset
        self.attack_args = attack_args
        self.attack_log_manager = None

        # This is to be set if loading from a checkpoint
        self._checkpoint = None

    def attack_dataset(self):
        """Attack the dataset.
        Returns:
            :obj:`list[AttackResult]` - List of :class:`~customattack.attack_results.AttackResult` obtained after attacking the given dataset..
        """
        # if self.attack_args.silent:
        #     logger.setLevel(logging.ERROR)
        #
        # if self.attack_args.query_budget:
        #     self.attack.goal_function.query_budget = self.attack_args.query_budget
        #
        if not self.attack_log_manager:
            self.attack_log_manager = AttackArgs.create_loggers_from_args(
                self.attack_args
            )

        customattack.shared.utils.set_seed(self.attack_args.random_seed)
        if self.dataset.shuffled and self.attack_args.checkpoint_interval:
            # Not allowed b/c we cannot recover order of shuffled data
            raise ValueError(
                "Cannot use `--checkpoint-interval` with dataset that has been internally shuffled."
            )

        self.attack_args.num_examples = (
            len(self.dataset)
            if self.attack_args.num_examples == -1
            else self.attack_args.num_examples
        )
        # if self.attack_args.parallel:
        #     if torch.cuda.device_count() == 0:
        #         raise Exception(
        #             "Found no GPU on your system. To run attacks in parallel, GPU is required."
        #         )
        #     self._attack_parallel()
        # else:
        #     self._attack()
        #
        # if self.attack_args.silent:
        #     logger.setLevel(logging.INFO)

        return self.attack_log_manager.results
