"""
Public API.

Tokens defined here are imported in generated test code.
Any change to the APIs defined here are breaking changes!
"""
import json
from dataclasses import dataclass, field
from typing import Any, Dict


from pact_testgen.models import PactResponse
from pact_testgen.verify import create_pactman_pact, result_factory
from pactman.verifier.verify import ResponseVerifier


@dataclass
class Response:
    """
    Requests-like Response class.
    """

    text: str
    headers: Dict[str, Any] = field(default_factory=dict)
    status_code: int = 200

    @classmethod
    def from_django_response(cls, response):
        return cls(
            text=response.content,
            headers=dict(response.headers),
            status_code=response.status_code,
        )

    def json(self):
        return json.loads(self.text)


def verify_response(
    consumer_name: str,
    provider_name: str,
    pact_response: Dict[str, Any],
    actual_response: Response,
    version: str = "3.0.0",
) -> bool:
    """
    Returns whether the actual response received from the API matches
    the contract specified in the supplied pact
    """
    # TODO: Get version from the actual Pactfile

    # We could do this conversion in generated code, but doing it here
    # eliminates the need for importing two classes named Response
    # in the generated code.
    pact_response = PactResponse(**pact_response)
    pactman_pact = create_pactman_pact(consumer_name, provider_name, version)
    result = result_factory()
    verifier = ResponseVerifier(
        pactman_pact, pact_response.dict(exclude_none=True), result
    )
    return verifier.verify(actual_response)
