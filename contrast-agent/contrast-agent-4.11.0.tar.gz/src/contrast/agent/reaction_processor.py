# -*- coding: utf-8 -*-
# Copyright © 2021 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
from contrast.agent.disable_reaction import DisableReaction
from contrast.api.settings_pb2 import Reaction

from contrast.extern import structlog as logging

logger = logging.getLogger("contrast")


class ReactionProcessor(object):
    @staticmethod
    def process(application_settings, settings):
        if (
            application_settings is None
            or settings is None
            or application_settings.reactions is None
            or len(application_settings.reactions) == 0
        ):
            return

        for reaction in application_settings.reactions:
            logger.debug("Received the following reaction: %s", reaction.operation)

            if reaction.operation == Reaction.DISABLE:
                DisableReaction.run(settings)
