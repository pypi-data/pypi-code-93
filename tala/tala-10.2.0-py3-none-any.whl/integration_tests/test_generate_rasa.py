import pytest
import re
import os

from tala.nl.languages import SUPPORTED_RASA_LANGUAGES

from .expected_generate_rasa_output import EXPECTED_BOILERPLATE
from .console_script_mixin import ConsoleScriptTestMixin


class TestGenerateRASAIntegration(ConsoleScriptTestMixin):
    def setup(self):
        super(TestGenerateRASAIntegration, self).setup()

    @pytest.mark.parametrize("language", SUPPORTED_RASA_LANGUAGES)
    def test_that_generating_boilerplate_ddd_succeeds(self, language):
        self._given_created_ddd_in_a_target_dir()
        with self._given_changed_directory_to_ddd_folder():
            self._given_added_grammar(language)
        with self._given_changed_directory_to_target_dir():
            self._given_added_language(language)
        self._then_result_is_successful()

    def _when_generating(self, language="eng"):
        self._run_tala_with(["generate", "rasa", "test_ddd", language])

    @pytest.mark.parametrize("language", SUPPORTED_RASA_LANGUAGES)
    def test_stdout_when_generating_boilerplate_ddd(self, language):
        self._given_created_ddd_in_a_target_dir()
        with self._given_changed_directory_to_ddd_folder():
            self._given_added_grammar(language)
        with self._given_changed_directory_to_target_dir():
            self._given_added_language(language)
            self._when_running_command(f"tala generate rasa test_ddd {language}")
        self._then_stdout_matches(EXPECTED_BOILERPLATE[language])

    def test_stdout_when_generating_ddd_with_an_action(self):
        self._given_created_ddd_in_a_target_dir()
        with self._given_changed_directory_to_ddd_folder():
            self._given_rgl_is_enabled()
            self._given_ontology_contains("""
<ontology name="TestDddOntology">
  <action name="call"/>
</ontology>""")
            self._given_grammar_contains(
                """
<grammar>
  <action name="call">
    <verb-phrase>
      <verb ref="call"/>
    </verb-phrase>
  </action>
  <lexicon>
    <verb id="call">
      <infinitive>call</infinitive>
    </verb>
  </lexicon>
  <request action="call"><utterance>make a call</utterance></request>
</grammar>"""
            )
        with self._given_changed_directory_to_target_dir():
            self._given_ddd_verifies_successfully()
            self._when_running_command("tala generate rasa test_ddd eng")
        self._then_stdout_matches(
            r'''- intent: test_ddd:action::call
  examples: |
    - make a call

- intent: NEGATIVE
  examples: |
    - aboard
    - about
''')  # yapf: disable  # noqa: W293

    def test_warning_when_generating_ddd_with_an_action_not_in_grammar(self):
        self._given_created_ddd_in_a_target_dir()
        with self._given_changed_directory_to_ddd_folder():
            self._given_rgl_is_enabled()
            self._given_ontology_contains(
                """
<ontology name="TestDddOntology">
  <action name="call"/>
  <action name="call_not_in_grammar"/>
</ontology>"""
            )
            self._given_grammar_contains(
                """
<grammar>
  <action name="call">
    <verb-phrase>
      <verb ref="call"/>
    </verb-phrase>
  </action>
  <lexicon>
    <verb id="call">
      <infinitive>call</infinitive>
    </verb>
  </lexicon>
  <request action="call"><utterance>make a call</utterance></request>
</grammar>"""
            )
        with self._given_changed_directory_to_target_dir():
            self._given_ddd_verifies_successfully()
            self._when_running_command("tala generate rasa test_ddd eng")
        self._then_stderr_matches(
            r'''UserWarning: Grammar contains no entries for action 'call_not_in_grammar', so training data will not be generated.'''
        )

    def _given_ddd_verifies_successfully(self):
        self._run_tala_with(["verify"])

    def test_generating_for_unknown_ddd(self):
        self._given_created_ddd_in_a_target_dir()
        with self._given_changed_directory_to_target_dir():
            self._when_running_command("tala generate rasa unknown-ddd eng")
        self._then_stderr_matches("UnexpectedDDDException: Expected DDD 'unknown-ddd' to exist but it didn't")

    def test_generating_for_unknown_language(self):
        self._given_created_ddd_in_a_target_dir()
        with self._given_changed_directory_to_target_dir():
            self._when_running_command("tala generate rasa test_ddd unknown-language")
        self._then_stderr_matches("tala generate rasa: error: argument language: invalid choice: 'unknown-language'")

    def test_generating_for_unsupported_language(self):
        self._given_created_ddd_in_a_target_dir()
        with self._given_changed_directory_to_target_dir():
            self._when_running_command("tala generate rasa test_ddd pes")
        self._then_stderr_matches(
            r"Expected one of the supported languages \['eng'\] in backend config "
            "'backend.config.json', but got 'pes'"
        )

    def test_stdout_when_generating_ddd_with_action_and_question_and_sortal_and_propositional_answers_without_rgl(self):
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
            self._given_ddd_verifies_successfully()
            self._when_running_command("tala generate rasa test_ddd eng")
        self._then_stdout_contains(
            '''- intent: test_ddd:action::buy
  examples: |
    - buy apples
    - buy 0 apples
    - buy 1224 apples
    - buy 99 apples
    - buy a hundred and fifty seven apples
    - buy three apples
    - buy two thousand fifteen apples

- intent: test_ddd:question::phone_number_of_contact
  examples: |
    - tell me a phone number
    - what is [John](test_ddd.sort.contact)'s number
    - tell me [John](test_ddd.sort.contact)'s number

- intent: test_ddd:answer
  examples: |
    - 0
    - 99
    - 1224
    - a hundred and fifty seven
    - three
    - two thousand fifteen
    - [John](test_ddd.sort.contact)
    - yes 0
    - no 99

- intent: test_ddd:answer_negation
  examples: |
    - not 0
    - not 99
    - not 1224
    - not a hundred and fifty seven
    - not three
    - not two thousand fifteen
    - not [John](test_ddd.sort.contact)

- intent: NEGATIVE
  examples: |
    - aboard
    - about
''')  # yapf: disable  # noqa: W293

    def test_stdout_when_generating_ddd_with_user_targeted_action_no_rgl(self):
        self._given_created_ddd_in_a_target_dir()
        with self._given_changed_directory_to_ddd_folder():
            self._given_ontology_contains(
                """
<ontology name="TestDddOntology">
  <action name="troubleshoot"/>
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
  <goal type="perform" action="troubleshoot">
    <plan>
      <get_done action="restart_phone"/>
      <get_done action="shred_phone"/>
      <get_done action="dump_phone"/>
    </plan>
  </goal>
</domain>"""
            )
            self._given_grammar_contains(
                """
<grammar>
  <action name="troubleshoot">
    <one-of>
      <item>there's something wrong with my phone</item>
      <item>i have a problem with my phone</item>
    </one-of>
  </action>
  <report action="restart_phone" status="done" speaker="user">
     <one-of>
        <item>i've restarted the phone</item>
        <item>the phone is restarted</item>
     </one-of>
  </report>
  <report action="shred_phone" status="done" speaker="user">
     the phone is dead
  </report>
</grammar>"""
            )
        with self._given_changed_directory_to_target_dir():
            self._given_ddd_verifies_successfully()
            self._when_running_command("tala generate rasa test_ddd eng")
        self._then_stdout_contains(
            '''- intent: test_ddd:action::troubleshoot
  examples: |
    - there's something wrong with my phone
    - i have a problem with my phone

- intent: test_ddd:user_report::restart_phone
  examples: |
    - i've restarted the phone
    - the phone is restarted

- intent: test_ddd:user_report::shred_phone
  examples: |
    - the phone is dead

- intent: NEGATIVE
  examples: |
    - aboard
    - about
''')  # yapf: disable  # noqa: W293

    def _then_result_matches(self, expected_contents):
        assert re.search(expected_contents, self._stdout, re.UNICODE) is not None, \
            f"Expected contents to match {expected_contents} but got {self._stdout}"

    def test_stdout_when_generating_ddd_with_action_and_question_and_sortal_and_propositional_slots_with_max_instances_per_grammar_entry(
        self
    ):
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
  <individual name="contact_mary" sort="contact"/>
  <individual name="contact_andy" sort="contact"/>
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
  <individual name="contact_mary">Mary</individual>
  <individual name="contact_andy">Andy</individual>
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
            self._given_ddd_verifies_successfully()
            self._when_running_command("tala generate rasa test_ddd eng -n 2")
        self._then_result_matches(
            r'''- intent: test_ddd:action::buy
  examples: |
    - buy apples
    - buy ([\d\w]+\s?)+ apples
    - buy ([\d\w]+\s?)+ apples

- intent: test_ddd:question::phone_number_of_contact
  examples: |
    - tell me a phone number
    - what is \[[A-Za-z]+\]\(test_ddd.sort.contact\)'s number
    - what is \[[A-Za-z]+\]\(test_ddd.sort.contact\)'s number
    - tell me \[[A-Za-z]+\]\{"entity": "test_ddd.sort.contact", "role": "test_ddd.predicate.selected_contact"\}'s number
    - tell me \[[A-Za-z]+\]\{"entity": "test_ddd.sort.contact", "role": "test_ddd.predicate.selected_contact"\}'s number

- intent: test_ddd:answer
  examples: |
    - 0
    - 99
    - 1224
    - a hundred and fifty seven
    - three
    - two thousand fifteen
    - \[John\]\(test_ddd.sort.contact\)
    - \[Mary\]\(test_ddd.sort.contact\)
    - \[Andy\]\(test_ddd.sort.contact\)

- intent: test_ddd:answer_negation
  examples: |
    - not 0
    - not 99
    - not 1224
    - not a hundred and fifty seven
    - not three
    - not two thousand fifteen
    - not \[John\]\(test_ddd.sort.contact\)
    - not \[Mary\]\(test_ddd.sort.contact\)
    - not \[Andy\]\(test_ddd.sort.contact\)

- intent: NEGATIVE
  examples: |
    - aboard
    - about
''')  # yapf: disable  # noqa: W293

    def test_override_examples_for_builtin_sort(self):
        self._given_created_ddd_in_a_target_dir()
        with self._given_changed_directory_to_ddd_folder():
            self._given_ontology_contains(
                """
<ontology name="TestDddOntology">
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
  <action name="buy">
    <one-of>
      <item>buy apples</item>
      <item>buy <slot type="individual" sort="integer"/> apples</item>
      <item>buy <slot type="individual" predicate="selected_amount"/> apples</item>
    </one-of>
  </action>
</grammar>"""
            )
        with self._given_changed_directory_to_target_dir():
            self._given_ddd_verifies_successfully()
            self._given_file_contains("integer_examples.csv", "1\none\n")
            self._when_running_command("tala generate rasa test_ddd eng --entity-examples integer:integer_examples.csv")
        self._then_stdout_contains(
            '''- intent: test_ddd:action::buy
  examples: |
    - buy apples
    - buy 1 apples
    - buy one apples

- intent: test_ddd:answer
  examples: |
    - 1
    - one
    - yes 1
    - no one

- intent: test_ddd:answer_negation
  examples: |
    - not 1
    - not one

''')  # yapf: disable  # noqa: W293

    def test_lookup_table_for_custom_sort(self):
        self._given_created_ddd_in_a_target_dir()
        with self._given_changed_directory_to_ddd_folder():
            self._given_ontology_contains(
                """
<ontology name="TestDddOntology">
  <sort name="postal_area"/>
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
</domain>"""
            )
            self._given_grammar_contains("""
<grammar>
</grammar>""")
        with self._given_changed_directory_to_target_dir():
            self._given_ddd_verifies_successfully()
            self._given_file_contains("postal_areas.csv", "Abbekås\nAbisko\n")
            self._when_running_command("tala generate rasa test_ddd eng --lookup-entries postal_area:postal_areas.csv")
        self._then_stdout_contains(
            '''- lookup: test_ddd.sort.postal_area
  examples: |
    - Abbekås
    - Abisko
''')  # yapf: disable  # noqa: W293

    def test_generate_examples_for_custom_sort_from_lookup_data(self):
        self._given_created_ddd_in_a_target_dir()
        with self._given_changed_directory_to_ddd_folder():
            self._given_ontology_contains(
                """
<ontology name="TestDddOntology">
  <action name="send_parcel"/>
  <sort name="postal_area"/>
  <predicate name="desired_postal_area" sort="postal_area"/>
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
  <goal type="perform" action="send_parcel">
    <plan>
      <findout type="wh_question" predicate="desired_postal_area"/>
      <invoke_service_action name="Send" postconfirm="true"/>
    </plan>
  </goal>
</domain>"""
            )
            self._given_grammar_contains(
                """
<grammar>
  <action name="send_parcel">
    <one-of>
      <item>send parcel</item>
      <item>send parcel to <slot type="individual" sort="postal_area"/></item>
      <item>send parcel to <slot type="individual" predicate="desired_postal_area"/></item>
    </one-of>
  </action>
</grammar>"""
            )
        with self._given_changed_directory_to_target_dir():
            self._given_ddd_verifies_successfully()
            self._given_file_contains("postal_areas.csv", "Abbekås\nAbisko\n")
            self._when_running_command("tala generate rasa test_ddd eng --lookup-entries postal_area:postal_areas.csv")
        self._then_stdout_contains(
            '''- intent: test_ddd:action::send_parcel
  examples: |
    - send parcel
    - send parcel to [Abbekås](test_ddd.sort.postal_area)
    - send parcel to [Abisko](test_ddd.sort.postal_area)
    - send parcel to [Abbekås](test_ddd.sort.postal_area)
    - send parcel to [Abisko](test_ddd.sort.postal_area)

- intent: test_ddd:answer
  examples: |
    - [Abbekås](test_ddd.sort.postal_area)
    - [Abisko](test_ddd.sort.postal_area)
    - yes [Abbekås](test_ddd.sort.postal_area)
    - no [Abisko](test_ddd.sort.postal_area)

- intent: test_ddd:answer_negation
  examples: |
    - not [Abbekås](test_ddd.sort.postal_area)
    - not [Abisko](test_ddd.sort.postal_area)
''')  # yapf: disable  # noqa: W293

    def test_generate_examples_for_custom_sort_from_lookup_data_randomly_selected_subset(self):
        self._given_created_ddd_in_a_target_dir()
        with self._given_changed_directory_to_ddd_folder():
            self._given_ontology_contains(
                """
<ontology name="TestDddOntology">
  <action name="send_parcel"/>
  <sort name="postal_area"/>
  <predicate name="desired_postal_area" sort="postal_area"/>
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
  <goal type="perform" action="send_parcel">
    <plan>
      <findout type="wh_question" predicate="desired_postal_area"/>
      <invoke_service_action name="Send" postconfirm="true"/>
    </plan>
  </goal>
</domain>"""
            )
            self._given_grammar_contains(
                """
<grammar>
  <action name="send_parcel">
    <one-of>
      <item>send parcel</item>
      <item>send parcel to <slot type="individual" sort="postal_area"/></item>
      <item>send parcel to <slot type="individual" predicate="desired_postal_area"/></item>
    </one-of>
  </action>
</grammar>"""
            )
        with self._given_changed_directory_to_target_dir():
            self._given_ddd_verifies_successfully()
            self._given_file_contains("postal_areas.csv", "Abbekås\nAbisko\nNödinge\nSvanesund\n")
            self._given_random_seed(1)
            self._when_running_command(
                "tala generate rasa test_ddd eng -n 2 --lookup-entries postal_area:postal_areas.csv"
            )
        self._then_stdout_contains(
            '''- intent: test_ddd:action::send_parcel
  examples: |
    - send parcel
    - send parcel to [Abbekås](test_ddd.sort.postal_area)
    - send parcel to [Nödinge](test_ddd.sort.postal_area)
    - send parcel to [Nödinge](test_ddd.sort.postal_area)
    - send parcel to [Svanesund](test_ddd.sort.postal_area)

- intent: test_ddd:answer
  examples: |
    - [Nödinge](test_ddd.sort.postal_area)
    - [Abbekås](test_ddd.sort.postal_area)
    - yes [Nödinge](test_ddd.sort.postal_area)
    - no [Abbekås](test_ddd.sort.postal_area)

- intent: test_ddd:answer_negation
  examples: |
    - not [Abbekås](test_ddd.sort.postal_area)
    - not [Svanesund](test_ddd.sort.postal_area)
''')  # yapf: disable  # noqa: W293

    def _given_random_seed(self, random_seed):
        os.putenv("TALA_GENERATE_SEED", "1")

    def test_generate_examples_for_custom_sort_from_external_data(self):
        self._given_created_ddd_in_a_target_dir()
        with self._given_changed_directory_to_ddd_folder():
            self._given_ontology_contains(
                """
<ontology name="TestDddOntology">
  <action name="send_parcel"/>
  <sort name="postal_area"/>
  <predicate name="desired_postal_area" sort="postal_area"/>
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
  <goal type="perform" action="send_parcel">
    <plan>
      <findout type="wh_question" predicate="desired_postal_area"/>
      <invoke_service_action name="Send" postconfirm="true"/>
    </plan>
  </goal>
</domain>"""
            )
            self._given_grammar_contains(
                """
<grammar>
  <action name="send_parcel">
    <one-of>
      <item>send parcel</item>
      <item>send parcel to <slot type="individual" sort="postal_area"/></item>
      <item>send parcel to <slot type="individual" predicate="desired_postal_area"/></item>
    </one-of>
  </action>
</grammar>"""
            )
        with self._given_changed_directory_to_target_dir():
            self._given_ddd_verifies_successfully()
            self._given_file_contains("postal_areas.csv", "Abbekås\nAbisko\nNödinge\nSvanesund\n")
            self._given_random_seed(1)
            self._when_running_command(
                "tala generate rasa test_ddd eng -n 2 --entity-examples postal_area:postal_areas.csv"
            )
        self._then_stdout_contains(
            '''- intent: test_ddd:action::send_parcel
  examples: |
    - send parcel
    - send parcel to [Abbekås](test_ddd.sort.postal_area)
    - send parcel to [Nödinge](test_ddd.sort.postal_area)
    - send parcel to [Nödinge](test_ddd.sort.postal_area)
    - send parcel to [Svanesund](test_ddd.sort.postal_area)

- intent: test_ddd:answer
  examples: |
    - [Abbekås](test_ddd.sort.postal_area)
    - [Abisko](test_ddd.sort.postal_area)
    - [Nödinge](test_ddd.sort.postal_area)
    - [Svanesund](test_ddd.sort.postal_area)
    - yes [Abbekås](test_ddd.sort.postal_area)
    - no [Abisko](test_ddd.sort.postal_area)

- intent: test_ddd:answer_negation
  examples: |
    - not [Abbekås](test_ddd.sort.postal_area)
    - not [Abisko](test_ddd.sort.postal_area)
    - not [Nödinge](test_ddd.sort.postal_area)
    - not [Svanesund](test_ddd.sort.postal_area)
''')  # yapf: disable  # noqa: W293

    def test_exclude_builtin_sort_from_training_data(self):
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
  <individual name="contact_mary" sort="contact"/>
  <individual name="contact_andy" sort="contact"/>
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
  <individual name="contact_mary">Mary</individual>
  <individual name="contact_andy">Andy</individual>
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
            self._given_ddd_verifies_successfully()
            self._given_random_seed(1)
            self._when_running_command("tala generate rasa test_ddd eng --exclude-sort integer")
        self._then_stdout_contains(
            r'''- intent: test_ddd:action::buy
  examples: |
    - buy apples

- intent: test_ddd:question::phone_number_of_contact
  examples: |
    - tell me a phone number
    - what is [Andy](test_ddd.sort.contact)'s number
    - what is [John](test_ddd.sort.contact)'s number
    - what is [Mary](test_ddd.sort.contact)'s number
    - tell me [Andy](test_ddd.sort.contact)'s number
    - tell me [John](test_ddd.sort.contact)'s number
    - tell me [Mary](test_ddd.sort.contact)'s number

- intent: test_ddd:answer
  examples: |
    - [John](test_ddd.sort.contact)
    - [Mary](test_ddd.sort.contact)
    - [Andy](test_ddd.sort.contact)
    - yes [John](test_ddd.sort.contact)
    - no [Mary](test_ddd.sort.contact)

- intent: test_ddd:answer_negation
  examples: |
    - not [John](test_ddd.sort.contact)
    - not [Mary](test_ddd.sort.contact)
    - not [Andy](test_ddd.sort.contact)

- intent: NEGATIVE
  examples: |
    - aboard
    - about
    - above
    - across
    - after
    - against
    - along
    - among
    - as
    - at
    - on
    - atop
    - before
    - behind
    - below
    - beneath
    - beside
    - between
    - beyond
    - but
    - by
    - come
    - down
    - during
    - except
    - for
    - from
    - in
    - inside
    - into
    - less
    - like
    - near
    - of
    - off
    - on
    - onto
    - opposite
    - out
    - outside
    - over
    - past
    - save
    - short
    - since
    - than
    - then
    - through
    - throughout
    - to
    - toward
    - under
    - underneath
    - unlike
    - until
    - up
    - upon
    - with
    - within
    - without
    - worth
    - is
    - it
    - the
    - a
    - am
    - are
    - them
    - this
    - that
    - I
    - you
    - he
    - she
    - they
    - them
    - his
    - her
    - my
    - mine
    - their
    - your
    - us
    - our
    - how
    - how's
    - how is
    - how's the
    - how is the
    - when
    - when's
    - when is
    - when is the
    - when's the
    - what
    - what is
    - what's
    - what's the
    - what is the
    - why
    - why is
    - why's
    - why is the
    - why's the
    - do
    - make
    - tell
    - start
    - stop
    - enable
    - disable
    - raise
    - lower
    - decrease
    - increase
    - act
    - determine
    - say
    - ask
    - go
    - shoot
    - wait
    - hang on
    - ok
    - show
    - help

- intent: answer:yes
  examples: |
    - yes
    - yeah
    - yep
    - sure
    - ok
    - of course
    - very well
    - fine
    - right
    - excellent
    - okay
    - perfect
    - I think so

- intent: answer:no
  examples: |
    - no
    - nope
    - no thanks
    - no thank you
    - negative
    - don't want to
    - don't
    - do not
    - please don't

- intent: request:top
  examples: |
    - forget it
    - never mind
    - get me out of here
    - start over
    - beginning
    - never mind that
    - restart

- intent: request:up
  examples: |
    - go back
    - back
    - previous
    - back to the previous
    - go to the previous
    - go back to the previous one

- intent: request:how
  examples: |
    - how do I do that
    - how
    - can you tell me how to do that
    - I don't know how should I do that
    - how can I do that

- intent: report:done
  examples: |
    - I'm done
    - done
    - ready
    - it's ready
    - I'm ready
    - completed
    - check
    - I have finished
    - finished
    - done and done
    - it's done now
    - okay next
    - next
    - next instruction

- intent: icm:per*neg
  examples: |
    - repeat
    - repeat it
    - repeat that
    - pardon
    - sorry
    - can you repeat that
    - excuse me
    - what was that
    - what did you say
    - come again

- intent: icm:acc*neg:issue
  examples: |
    - I don't know
    - I don't know that
    - it doesn't matter

- intent: thanks
  examples: |
    - thank you
    - thank you very much
    - thanks
    - big thanks
    - thanks a lot

- intent: greet
  examples: |
    - hello
    - hi
    - good day
    - what's up
    - good evening
    - good morning
    - hey

- synonym: test_ddd:contact_john
  examples: |
    - John

- synonym: test_ddd:contact_mary
  examples: |
    - Mary

- synonym: test_ddd:contact_andy
  examples: |
    - Andy
''')  # yapf: disable  # noqa: W293

    def test_exclude_custom_sort_from_training_data(self):
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
  <individual name="contact_mary" sort="contact"/>
  <individual name="contact_andy" sort="contact"/>
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
  <individual name="contact_mary">Mary</individual>
  <individual name="contact_andy">Andy</individual>
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
            self._given_ddd_verifies_successfully()
            self._given_random_seed(1)
            self._when_running_command("tala generate rasa test_ddd eng --exclude-sort contact")
        self._then_stdout_contains(
            r'''- intent: test_ddd:action::buy
  examples: |
    - buy apples
    - buy 0 apples
    - buy 1224 apples
    - buy 99 apples
    - buy a hundred and fifty seven apples
    - buy three apples
    - buy two thousand fifteen apples

- intent: test_ddd:question::phone_number_of_contact
  examples: |
    - tell me a phone number

- intent: test_ddd:answer
  examples: |
    - 0
    - 99
    - 1224
    - a hundred and fifty seven
    - three
    - two thousand fifteen
    - yes 0
    - no 99

- intent: test_ddd:answer_negation
  examples: |
    - not 0
    - not 99
    - not 1224
    - not a hundred and fifty seven
    - not three
    - not two thousand fifteen

- intent: NEGATIVE
  examples: |
    - aboard
    - about
    - above
    - across
    - after
    - against
    - along
    - among
    - as
    - at
    - on
    - atop
    - before
    - behind
    - below
    - beneath
    - beside
    - between
    - beyond
    - but
    - by
    - come
    - down
    - during
    - except
    - for
    - from
    - in
    - inside
    - into
    - less
    - like
    - near
    - of
    - off
    - on
    - onto
    - opposite
    - out
    - outside
    - over
    - past
    - save
    - short
    - since
    - than
    - then
    - through
    - throughout
    - to
    - toward
    - under
    - underneath
    - unlike
    - until
    - up
    - upon
    - with
    - within
    - without
    - worth
    - is
    - it
    - the
    - a
    - am
    - are
    - them
    - this
    - that
    - I
    - you
    - he
    - she
    - they
    - them
    - his
    - her
    - my
    - mine
    - their
    - your
    - us
    - our
    - how
    - how's
    - how is
    - how's the
    - how is the
    - when
    - when's
    - when is
    - when is the
    - when's the
    - what
    - what is
    - what's
    - what's the
    - what is the
    - why
    - why is
    - why's
    - why is the
    - why's the
    - do
    - make
    - tell
    - start
    - stop
    - enable
    - disable
    - raise
    - lower
    - decrease
    - increase
    - act
    - determine
    - say
    - ask
    - go
    - shoot
    - wait
    - hang on
    - ok
    - show
    - help

- intent: answer:yes
  examples: |
    - yes
    - yeah
    - yep
    - sure
    - ok
    - of course
    - very well
    - fine
    - right
    - excellent
    - okay
    - perfect
    - I think so

- intent: answer:no
  examples: |
    - no
    - nope
    - no thanks
    - no thank you
    - negative
    - don't want to
    - don't
    - do not
    - please don't

- intent: request:top
  examples: |
    - forget it
    - never mind
    - get me out of here
    - start over
    - beginning
    - never mind that
    - restart

- intent: request:up
  examples: |
    - go back
    - back
    - previous
    - back to the previous
    - go to the previous
    - go back to the previous one

- intent: request:how
  examples: |
    - how do I do that
    - how
    - can you tell me how to do that
    - I don't know how should I do that
    - how can I do that

- intent: report:done
  examples: |
    - I'm done
    - done
    - ready
    - it's ready
    - I'm ready
    - completed
    - check
    - I have finished
    - finished
    - done and done
    - it's done now
    - okay next
    - next
    - next instruction

- intent: icm:per*neg
  examples: |
    - repeat
    - repeat it
    - repeat that
    - pardon
    - sorry
    - can you repeat that
    - excuse me
    - what was that
    - what did you say
    - come again

- intent: icm:acc*neg:issue
  examples: |
    - I don't know
    - I don't know that
    - it doesn't matter

- intent: thanks
  examples: |
    - thank you
    - thank you very much
    - thanks
    - big thanks
    - thanks a lot

- intent: greet
  examples: |
    - hello
    - hi
    - good day
    - what's up
    - good evening
    - good morning
    - hey
''')  # yapf: disable  # noqa: W293

    def test_warning_when_generating_ddd_with_an_action_with_one_entry(self):
        self._given_created_ddd_in_a_target_dir()
        with self._given_changed_directory_to_ddd_folder():
            self._given_ontology_contains(
                """
<ontology name="TestDddOntology">
  <action name="call"/>
  <action name="call_one_entry_in_grammar"/>
</ontology>"""
            )
            self._given_grammar_contains(
                """
<grammar>
  <action name="call">
    <one-of>
      <item>make a call</item>
      <item>i want to call</item>
    </one-of>
  </action>
  <action name="call_one_entry_in_grammar">call another person</action>
</grammar>"""
            )
        with self._given_changed_directory_to_target_dir():
            self._given_ddd_verifies_successfully()
            self._when_running_command("tala generate rasa test_ddd eng")
        self._then_stderr_matches(
            r'''UserWarning: Grammar contains one entry for action 'call_one_entry_in_grammar', so training data will not be generated.'''
        )

    def test_generate_entities_with_roles(self):
        self._given_created_ddd_in_a_target_dir()
        with self._given_changed_directory_to_ddd_folder():
            self._given_ontology_contains(
                """
<ontology name="TestDddOntology">
  <action name="send_parcel"/>
  <sort name="postal_area"/>
  <predicate name="desired_postal_area" sort="postal_area"/>
  <predicate name="another_postal_area" sort="postal_area"/>
  <individual name="postal_area_abbekas" sort="postal_area"/>
  <individual name="postal_area_nodinge" sort="postal_area"/>
  <individual name="postal_area_svanesund" sort="postal_area"/>
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
  <goal type="perform" action="send_parcel">
    <plan>
      <findout type="wh_question" predicate="desired_postal_area"/>
      <findout type="wh_question" predicate="another_postal_area"/>
      <invoke_service_action name="Send" postconfirm="true"/>
    </plan>
  </goal>
</domain>"""
            )
            self._given_grammar_contains(
                """
<grammar>
  <action name="send_parcel">
    <one-of>
      <item>send a parcel</item>
      <item>send a parcel to <slot sort="postal_area"/></item>
      <item>send a parcel to <slot predicate="desired_postal_area"/></item>
      <item>send a parcel to <slot predicate="desired_postal_area"/> and another to <slot predicate="another_postal_area"/></item>
    </one-of>
  </action>
  <individual name="postal_area_abbekas">Abbekås</individual>
  <individual name="postal_area_nodinge">Nödinge</individual>
  <individual name="postal_area_svanesund">Svanesund</individual>
</grammar>"""
            )
        with self._given_changed_directory_to_target_dir():
            self._given_ddd_verifies_successfully()
            self._given_random_seed(1)
            self._when_running_command(
                "tala generate rasa test_ddd eng -n 2"
            )
        self._then_stdout_contains(
            '''- intent: test_ddd:action::send_parcel
  examples: |
    - send a parcel
    - send a parcel to [Abbekås](test_ddd.sort.postal_area)
    - send a parcel to [Svanesund](test_ddd.sort.postal_area)
    - send a parcel to [Nödinge](test_ddd.sort.postal_area)
    - send a parcel to [Svanesund](test_ddd.sort.postal_area)
    - send a parcel to [Abbekås]{"entity": "test_ddd.sort.postal_area", "role": "test_ddd.predicate.desired_postal_area"} and another to [Svanesund]{"entity": "test_ddd.sort.postal_area", "role": "test_ddd.predicate.another_postal_area"}
    - send a parcel to [Svanesund]{"entity": "test_ddd.sort.postal_area", "role": "test_ddd.predicate.desired_postal_area"} and another to [Nödinge]{"entity": "test_ddd.sort.postal_area", "role": "test_ddd.predicate.another_postal_area"}

- intent: test_ddd:answer
  examples: |
    - [Abbekås](test_ddd.sort.postal_area)
    - [Nödinge](test_ddd.sort.postal_area)
    - [Svanesund](test_ddd.sort.postal_area)
    - yes [Abbekås](test_ddd.sort.postal_area)
    - no [Nödinge](test_ddd.sort.postal_area)

- intent: test_ddd:answer_negation
  examples: |
    - not [Abbekås](test_ddd.sort.postal_area)
    - not [Nödinge](test_ddd.sort.postal_area)
    - not [Svanesund](test_ddd.sort.postal_area)
''')  # yapf: disable  # noqa: W293
