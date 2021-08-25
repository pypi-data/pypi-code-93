import json
from pathlib import Path

from .console_script_mixin import ConsoleScriptTestMixin


class TestGenerateAlexaIntegration(ConsoleScriptTestMixin):
    def setup(self):
        super(TestGenerateAlexaIntegration, self).setup()

    def test_that_generating_boilerplate_ddd_succeeds(self):
        self._given_created_ddd_in_a_target_dir()
        with self._given_changed_directory_to_target_dir():
            self._when_generating()
        self._then_result_is_successful()

    def _when_generating(self):
        self._run_tala_with(["generate", "alexa", "test_ddd", "eng"])

    def test_stdout_when_generating_ddd_with_action_and_question_and_sortal_and_propositional_answers(self):
        self._given_created_ddd_in_a_target_dir()
        with self._given_changed_directory_to_ddd_folder():
            self._given_ontology_contains(
                """
<ontology name="TestDddOntology">
  <sort name="contact"/>
  <sort name="phone_number" dynamic="true"/>
  <predicate name="phone_number_of_contact" sort="phone_number"/>
  <predicate name="selected_contact" sort="contact"/>
  <individual name="contact_john" sort="contact"/>
  <action name="buy"/>
  <predicate name="selected_amount" sort="integer"/>
</ontology>"""
            )
            self._given_domain_contains(
                """
<domain name="TestDddDomain">
  <goal type="perform" action="top">
    <plan>
      <forget_all/>
      <findout type="goal"/>
    </plan>
  </goal>
  <goal type="resolve" question_type="wh_question" predicate="phone_number_of_contact">
    <plan>
      <findout type="wh_question" predicate="selected_contact"/>
    </plan>
  </goal>
  <goal type="perform" action="buy">
    <plan>
      <findout type="wh_question" predicate="selected_amount"/>
      <invoke_service_action name="Buy" postconfirm="true"/>
    </plan>
  </goal>
</domain>"""
            )
            self._given_grammar_contains(
                """
<grammar>
  <question speaker="user" predicate="phone_number_of_contact">
    <one-of>
      <item>tell me a phone number</item>
      <item>what is <slot type="individual" sort="contact"/>'s number</item>
      <item>tell me <slot type="individual" predicate="selected_contact"/>'s number</item>
    </one-of>
  </question>
  <individual name="contact_john">John</individual>
  <action name="buy">
    <one-of>
      <item>
        <vp>
          <infinitive>buy</infinitive>
          <imperative>buy</imperative>
          <ing-form>buying</ing-form>
          <object>apples</object>
        </vp>
      </item>
      <item>buy apples</item>
      <item>buy <slot type="individual" sort="integer"/> apples</item>
      <item>buy <slot type="individual" predicate="selected_amount"/> apples</item>
    </one-of>
  </action>
</grammar>"""
            )
        with self._given_changed_directory_to_target_dir():
            self._when_running_command("tala generate alexa test_ddd eng")
        self._then_stdout_has_json({
            "interactionModel": {
                "languageModel": {
                    "intents": [
                        {
                            "name": "test_ddd_action_buy",
                            "samples": [
                                "buy apples",
                                "buy {test_ddd_sort_integer} apples",
                                "buy {test_ddd_predicate_selected_amount} apples"
                            ],
                            "slots": [
                                {
                                    "name": "test_ddd_sort_integer",
                                    "type": "AMAZON.NUMBER"
                                },
                                {
                                    "name": "test_ddd_predicate_selected_amount",
                                    "type": "AMAZON.NUMBER"
                                }
                            ]
                        },
                        {
                            "name": "test_ddd_question_phone_number_of_contact",
                            "samples": [
                                "tell me a phone number",
                                "what is {test_ddd_sort_contact}'s number",
                                "tell me {test_ddd_predicate_selected_contact}'s number"
                            ],
                            "slots": [
                                {
                                    "name": "test_ddd_sort_contact",
                                    "type": "test_ddd_sort_contact"
                                },
                                {
                                    "name": "test_ddd_predicate_selected_contact",
                                    "type": "test_ddd_sort_contact"
                                }
                            ]
                        },
                        {
                            "name": "test_ddd_answer",
                            "samples": [
                                "{test_ddd_sort_integer}",
                                "{test_ddd_sort_contact}",
                                "yes {test_ddd_sort_integer}",
                                "no {test_ddd_sort_contact}",
                            ],
                            "slots": [
                                {
                                    "name": "test_ddd_sort_integer",
                                    "type": "AMAZON.NUMBER"
                                },
                                {
                                    'name': 'test_ddd_sort_contact',
                                    'type': 'test_ddd_sort_contact'
                                }
                            ]
                        },
                        {
                            "name": "test_ddd_answer_negation",
                            "samples": [
                                "not {test_ddd_sort_integer}",
                                "not {test_ddd_sort_contact}",
                            ],
                            "slots": [
                                {
                                    "name": "test_ddd_sort_integer",
                                    "type": "AMAZON.NUMBER"
                                },
                                {
                                    'name': 'test_ddd_sort_contact',
                                    'type': 'test_ddd_sort_contact'
                                }
                            ]
                        },
                        {
                            "name": "AMAZON.YesIntent",
                            "samples": []
                        },
                        {
                            "name": "AMAZON.NoIntent",
                            "samples": []
                        },
                        {
                            "name": "AMAZON.CancelIntent",
                            "samples": []
                        },
                        {
                            "name": "AMAZON.StopIntent",
                            "samples": []
                        }
                    ],
                    "invocationName": "test_ddd",
                    "types": [
                        {
                            "name": "test_ddd_sort_contact",
                            "values": [
                                {
                                    "id": "contact_john",
                                    "name": {
                                        "synonyms": [],
                                        "value": "John",
                                    }
                                }
                            ]
                        }
                    ]
                }
            }
        })  # yapf: disable

    def _given_ontology_contains(self, new_content):
        old_content = """
<ontology name="TestDddOntology">
</ontology>"""
        self._replace_in_file(Path("ontology.xml"), old_content, new_content)

    def _given_grammar_contains(self, new_content):
        old_content = """
<grammar>

  <action name="top">
    <one-of>
      <item>main menu</item>
      <item>top</item>
      <item>beginning</item>
      <item>cancel</item>
      <item>forget it</item>
      <item>never mind</item>
      <item>abort</item>
    </one-of>
  </action>

  <action name="up">
    <one-of>
      <item>up</item>
      <item>back</item>
      <item>go back</item>
    </one-of>
  </action>

</grammar>"""
        self._replace_in_file(Path("grammar") / "grammar_eng.xml", old_content, new_content)

    def _then_stdout_has_json(self, expected_json):
        def unicodify(o):
            if isinstance(o, dict):
                return {str(key): unicodify(value) for key, value in list(o.items())}
            if isinstance(o, list):
                return [unicodify(element) for element in o]
            return str(o)

        actual_json = json.loads(self._stdout)
        assert actual_json == unicodify(expected_json)
