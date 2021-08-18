from abc import ABC
from typing import List, TYPE_CHECKING

from convo.core.actions.action import Action
from convo.shared.core.events import Event, OperationalLoop

if TYPE_CHECKING:
    from convo.core.channels import OutputSocket
    from convo.shared.core.domain import Domain
    from convo.core.nlg import NaturalLanguageGenerator
    from convo.shared.core.trackers import DialogueStateTracer


class LoopAct(Action, ABC):  # pytype: disable=base-class-error
    async def run(
        self,
        output_channel: "OutputSocket",
        nlg: "NaturalLanguageGenerator",
        tracker: "DialogueStateTracer",
        domain: "Domain",
    ) -> List[Event]:
        event = []

        if not await self.is_activated(output_channel, nlg, tracker, domain):
            event += self._by_default_activation_events()
            event += await self.activate(output_channel, nlg, tracker, domain)

        if not await self.is_done(output_channel, nlg, tracker, domain, event):
            event += await self.do(output_channel, nlg, tracker, domain, event)

        if await self.is_done(output_channel, nlg, tracker, domain, event):
            event += self._by_default_deactivation_event()
            event += await self.deactivate(
                output_channel, nlg, tracker, domain, event
            )

        return event

    async def is_activated(
        self,
        output_channel: "OutputSocket",
        nlg: "NaturalLanguageGenerator",
        tracker: "DialogueStateTracer",
        domain: "Domain",
    ) -> bool:
        # pytype: disable=attribute-error
        return tracker.activeLoopName == self.name()
        # pytype: enable=attribute-error

    # default implementation checks if form active
    def _by_default_activation_events(self) -> List[Event]:
        return [OperationalLoop(self.name())]  # pytype: disable=attribute-error

    async def activate(
        self,
        output_channel: "OutputSocket",
        nlg: "NaturalLanguageGenerator",
        tracker: "DialogueStateTracer",
        domain: "Domain",
    ) -> List[Event]:
        # can be overwritten
        return []

    async def do(
        self,
        output_channel: "OutputSocket",
        nlg: "NaturalLanguageGenerator",
        tracker: "DialogueStateTracer",
        domain: "Domain",
        events_so_far: List[Event],
    ) -> List[Event]:
        raise NotImplementedError()

    async def is_done(
        self,
        output_channel: "OutputSocket",
        nlg: "NaturalLanguageGenerator",
        tracker: "DialogueStateTracer",
        domain: "Domain",
        events_so_far: List[Event],
    ) -> bool:
        raise NotImplementedError()

    def _by_default_deactivation_event(self) -> List[Event]:
        return [OperationalLoop(None)]

    async def deactivate(
        self,
        output_channel: "OutputSocket",
        nlg: "NaturalLanguageGenerator",
        tracker: "DialogueStateTracer",
        domain: "Domain",
        events_so_far: List[Event],
    ) -> List[Event]:
        # can be overwritten
        return []
