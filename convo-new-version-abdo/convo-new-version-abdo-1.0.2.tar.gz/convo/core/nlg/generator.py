import logging
from typing import Optional, Union, Text, Any, Dict

import convo.shared.utils.common
from convo.shared.core.domain import Domain
from convo.utils.endpoints import EndpointConfiguration
from convo.shared.core.trackers import DialogueStateTracer

log = logging.getLogger(__name__)


class NaturalLanguageGenerator:
    """Generate bot utterances based on a dialogue state."""

    async def generate(
        self,
        template_name: Text,
        tracker: "DialogueStateTracer",
        output_channel: Text,
        **kwargs: Any,
    ) -> Optional[Dict[Text, Any]]:
        """Generate a response for the requested template.

        There are a lot of different methods to implement this, e.g. the
        generation can be based on templates or be fully ML based by feeding
        the dialogue state into a machine learning NLG model."""
        raise NotImplementedError

    @staticmethod
    def create(
        obj: Union["NaturalLanguageGenerator", EndpointConfiguration, None],
        domain: Optional[Domain],
    ) -> "NaturalLanguageGenerator":
        """Factory to create a generator."""

        if isinstance(obj, NaturalLanguageGenerator):
            return obj
        else:
            return _create_from_endpoint_configuration(obj, domain)


def _create_from_endpoint_configuration(
    endpoint_config: Optional[EndpointConfiguration] = None, _domain: Optional[Domain] = None
) -> "NaturalLanguageGenerator":
    """Given an endpoint configuration, create a proper NLG object."""

    _domain = _domain or Domain.empty()

    if endpoint_config is None:
        from convo.core.nlg import (  # pytype: disable=pyi-error
            TemplatedNaturalLanguageGenerator,
        )

        # this is the default type if no endpoint config is set
        generator_nlg = TemplatedNaturalLanguageGenerator(_domain.templates)
    elif endpoint_config.type is None or endpoint_config.type.lower() == "callback":
        from convo.core.nlg import (  # pytype: disable=pyi-error
            CallbackNaturalLangGenerator,
        )

        # this is the default type if no nlg type is set
        generator_nlg = CallbackNaturalLangGenerator(endpoint_config=endpoint_config)
    elif endpoint_config.type.lower() == "template":
        from convo.core.nlg import (  # pytype: disable=pyi-error
            TemplatedNaturalLanguageGenerator,
        )

        generator_nlg = TemplatedNaturalLanguageGenerator(_domain.templates)
    else:
        generator_nlg = _load_from_module_name_in_endpoint_configuration(endpoint_config, _domain)

    log.debug(f"Instantiated NLG to '{generator_nlg.__class__.__name__}'.")
    return generator_nlg


def _load_from_module_name_in_endpoint_configuration(
    endpoint_config: EndpointConfiguration, domain: Domain
) -> "NaturalLanguageGenerator":
    """Initializes a custom natural language generator.

    Args:
        domain: defines the universe in which the assistant operates
        endpoint_config: the specific natural language generator
    """

    try:
        nlg_classes = convo.shared.utils.common.class_name_from_module_path(
            endpoint_config.type
        )
        return nlg_classes(endpoint_config=endpoint_config, domain=domain)
    except (AttributeError, ImportError) as e:
        raise Exception(
            f"Could not find a class based on the module path "
            f"'{endpoint_config.type}'. Failed to create a "
            f"`NaturalLanguageGenerator` instance. Error: {e}"
        )
