"""Main module."""
from collections import defaultdict
from pathlib import Path
from typing import List

from pact_testgen.files import (
    load_pact_file,
    write_test_file,
    write_provider_state_file,
)
from pact_testgen.generators.django.generator import generate_tests
from pact_testgen.models import Pact, TestCase, TestFile


def run(
    base_class: str,
    pact_file: str,
    output_dir: Path,
    test_file_name="test_pact.py",
    provider_state_file_name="provider_states.py",
):
    """Loads the pact file, and writes the generated output files to output_dir"""
    pact = load_pact_file(pact_file)
    test_file = convert_to_test_cases(pact, base_class)
    test_file, provider_state_file = generate_tests(test_file)
    write_test_file(test_file, output_dir / test_file_name)
    write_test_file(provider_state_file, output_dir / provider_state_file_name)


def convert_to_test_cases(pact: Pact, base_class: str) -> TestFile:
    """
    Given a Pact file, create TestFile representations
    according to the following:


    - One test case per provider state name.

    - Each interaction for a given provider state name
      becomes a test method.
    """
    base_class_import_path, base_class = base_class.rsplit(".", 1)

    provider_states_interactions = defaultdict(list)

    for interaction in pact.interactions:
        # We need a hashable collection to key on, but also need to rememeber
        # name order so that test case names are deterministic based on the
        # order defined in the Pact contract.
        provider_state_key = frozenset([ps.name for ps in interaction.providerStates])
        provider_states_interactions[provider_state_key].append(interaction)

    cases = []

    for (
        _,
        interactions,
    ) in provider_states_interactions.items():
        cases.append(
            TestCase(
                # Interactions have been grouped by the set of
                # provider states, and we know there is at least
                # one interaction, so we can use the provider states
                # of the first interaction.
                provider_state_names=[ps.name for ps in interactions[0].providerStates],
                test_methods=interactions,
            )
        )

    return TestFile(
        base_class=base_class,
        consumer=pact.consumer,
        import_path=base_class_import_path,
        provider=pact.provider,
        test_cases=cases,
    )
