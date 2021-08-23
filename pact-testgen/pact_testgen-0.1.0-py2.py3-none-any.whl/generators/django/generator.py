import json
import os
from jinja2 import Environment, FileSystemLoader, select_autoescape
from typing import List, Tuple

from pact_testgen.generators.models import RequestArgs, TestMethodArgs
from pact_testgen.models import Interaction, TestCase, TestFile
from pact_testgen.utils import to_camel_case, to_snake_case

path = os.path.dirname(__file__) + "/templates"
env = Environment(
    loader=FileSystemLoader(searchpath=path), autoescape=select_autoescape()
)


def generate_tests(test_file: TestFile) -> Tuple[str, str]:
    cases = []
    provider_state_setup_functions = []
    consumer_name = test_file.consumer.name
    provider_name = test_file.provider.name

    for test_case in test_file.test_cases:
        args: List[TestMethodArgs] = []

        for method in test_case.test_methods:
            args.append(_build_method_args(method))

        methods = env.get_template("test_methods.jinja").render(
            args=args, consumer_name=consumer_name, provider_name=provider_name
        )

        setup_function_name = (
            f"setup_{to_snake_case(test_case.combined_provider_state_names)}"
        )

        case = env.get_template("test_case.jinja").render(
            ps_names=test_case.combined_provider_state_names,
            class_name=_get_test_class_name(test_case),
            file=test_file,
            methods=methods,
            setup_function_name=setup_function_name,
        )
        cases.append(case)
        provider_state_setup_functions.append(
            {
                "method_name": setup_function_name,
                "provider_states": test_case.provider_state_names,
            }
        )

    all_tests = env.get_template("test_file.jinja").render(
        file=test_file, cases=cases, setup_functions=provider_state_setup_functions
    )

    provider_states = env.get_template("provider_states.jinja").render(
        setup_functions=provider_state_setup_functions
    )
    return all_tests, provider_states


def _build_method_args(interaction: Interaction) -> TestMethodArgs:
    request_args = RequestArgs(
        method=interaction.request.method.value,
        path=interaction.request.path,
        data=json.dumps(interaction.request.body) if interaction.request.body else "",
    )

    test_method_args = TestMethodArgs(
        name=_get_test_method_name(interaction),
        expectation=repr(interaction.response.dict()),
        request=request_args,
    )

    return test_method_args


def _get_test_class_name(test_case: TestCase) -> str:
    return f"Test{to_camel_case(test_case.combined_provider_state_names)}"


def _get_test_method_name(interaction: Interaction) -> str:
    return f"test_{to_snake_case(interaction.description)}"
