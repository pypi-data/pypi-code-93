import copy
import logging

from convo.shared.core.trackers import DialogueStateTracer
from typing import Text, Any, Dict, Optional, List

from convo.core.nlg import interpolator  # pytype: disable=pyi-error
from convo.core.nlg.generator import NaturalLanguageGenerator

logger = logging.getLogger(__name__)


class TemplatedNaturalLanguageGenerator(NaturalLanguageGenerator):
    """Natural language generator that generates messages based on templates.

    The templates can use variables to customize the utterances based on the
    state of the dialogue."""

    def __init__(self, templates: Dict[Text, List[Dict[Text, Any]]]) -> None:
        self.templates = templates

    def _templates_for_utter_act(
        self, utter_action: Text, output_channel: Text
    ) -> List[Dict[Text, Any]]:
        """Return array of templates that fit the channel and action."""

        socket_templates = []
        by_default_templates = []

        for template in self.templates[utter_action]:
            if template.get("channel") == output_channel:
                socket_templates.append(template)
            elif not template.get("channel"):
                by_default_templates.append(template)

        # always prefer channel specific templates over default ones
        if socket_templates:
            return socket_templates
        else:
            return by_default_templates

    # noinspection PyUnusedLocal
    def _for_random_template(
        self, utter_action: Text, output_channel: Text
    ) -> Optional[Dict[Text, Any]]:
        """Select random template for the utter action from available ones.

        If channel-specific templates for the current output channel are given,
        only choose from channel-specific ones.
        """
        import numpy as np

        if utter_action in self.templates:
            suitable_templates = self._templates_for_utter_act(
                utter_action, output_channel
            )

            if suitable_templates:
                return np.random.choice(suitable_templates)
            else:
                return None
        else:
            return None

    async def create(
        self,
        template_name: Text,
        tracker: DialogueStateTracer,
        output_channel: Text,
        **kwargs: Any,
    ) -> Optional[Dict[Text, Any]]:
        """Generate a response for the requested template."""

        fill_slots_value = tracker.values_of_current_slot()
        return self.create_from_slots(
            template_name, fill_slots_value, output_channel, **kwargs
        )

    def create_from_slots(
        self,
        template_name: Text,
        fill_slots_value: Dict[Text, Any],
        output_channel: Text,
        **kwargs: Any,
    ) -> Optional[Dict[Text, Any]]:
        """Generate a response for the requested template."""

        # Fetching a random template for the passed template name
        s = copy.deepcopy(self._for_random_template(template_name, output_channel))
        # Filling the convo_slotsin the template and returning the template
        if s is not None:
            return self._fill_template_details(s, fill_slots_value, **kwargs)
        else:
            return None

    def _fill_template_details(
        self,
        template: Dict[Text, Any],
        fill_slots_value: Optional[Dict[Text, Any]] = None,
        **kwargs: Any,
    ) -> Dict[Text, Any]:
        """Combine slot values and key word arguments to fill templates."""

        # Getting the slot values in the template variables
        template_variables = self._templates_variables(fill_slots_value, kwargs)

        interpolate_by_keys = [
            "text",
            "image",
            "custom",
            "buttons",
            "attachment",
            "quick_replies",
        ]
        if template_variables:
            for key in interpolate_by_keys:
                if key in template:
                    template[key] = interpolator.fetch_interpolate(
                        template[key], template_variables
                    )
        return template

    @staticmethod
    def _templates_variables(
        fill_slots_value: Dict[Text, Any], kwargs: Dict[Text, Any]
    ) -> Dict[Text, Any]:
        """Combine slot values and key word arguments to fill templates."""

        if fill_slots_value is None:
            fill_slots_value = {}

        # Copying the filled convo_slotsin the template variables.
        template_vars = fill_slots_value.copy()
        template_vars.update(kwargs)
        return template_vars
