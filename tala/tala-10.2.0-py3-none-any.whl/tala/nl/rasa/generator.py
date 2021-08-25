import os
from io import StringIO
import warnings
from random import shuffle, sample, seed

from jinja2 import Template

from tala.model.action import TOP, UP, HOW
from tala.model.action_status import DONE
from tala.model.individual import Yes, No
from tala.model.move import ICMMove, IssueICMMove, Move
from tala.model.sort import STRING
from tala.nl.abstract_generator import AbstractGenerator, UnexpectedPropositionalEntityEncounteredException, \
    UnexpectedRequiredEntityException
from tala.nl.constants import ACTION_INTENT, QUESTION_INTENT, NEGATIVE_INTENT, USER_REPORT_INTENT
from tala.nl.generated_intent import GeneratedIntent, GeneratedBuiltinAnswerIntent, GeneratedBuiltinRequestIntent, \
    GeneratedBuiltinReportIntent
from tala.nl import languages

NEGATIVE_PERCEPTION_ICM = ICMMove(ICMMove.PER, polarity=ICMMove.NEG)
NEGATIVE_ISSUE_ACCEPTANCE_ICM = IssueICMMove(ICMMove.ACC, polarity=ICMMove.NEG)


class RasaGenerator(AbstractGenerator):
    def __init__(
        self,
        ddd,
        grammar_path,
        language_code,
        num_training_instances,
        custom_entity_examples_for_builtin_sorts={},
        lookup_entries={},
        excluded_sorts=[]
    ):
        AbstractGenerator.__init__(
            self, ddd, grammar_path, language_code, custom_entity_examples_for_builtin_sorts, lookup_entries,
            excluded_sorts
        )
        self._num_training_instances = num_training_instances
        random_seed = os.getenv("TALA_GENERATE_SEED")
        seed(random_seed)

    @property
    def _language(self):
        return languages.RASA_LANGUAGE[self._language_code]

    def stream(self, file_object):
        stream = self._generate_examples()
        return stream.dump(file_object)

    def generate(self):
        stream = self._generate_examples()
        string = StringIO()
        stream.dump(string)
        result = string.getvalue()
        string.close()
        return result

    def _format_action(self, name):
        return f"{ACTION_INTENT}::{name}"

    def _format_question(self, name):
        return f"{QUESTION_INTENT}::{name}"

    def _format_user_report(self, action):
        return f"{USER_REPORT_INTENT}::{action}"

    @property
    def _builtin_entity_template(self):
        return Template("{{ grammar_entry }}")

    @property
    def _entity_template_without_role(self):
        return Template("[{{ grammar_entry }}]({{ ddd }}.sort.{{ sort_name }})")

    @property
    def _entity_template_with_role(self):
        return Template(
            "[{{ grammar_entry }}]{\"entity\": \"{{ ddd }}.sort.{{ sort_name }}\", \"role\": \"{{ ddd }}.predicate.{{ predicate_name }}\"}"
        )

    def _generate_examples(self):
        examples = super(RasaGenerator, self)._generate_examples()

        data_template = Template(
            "version: \"2.0\"\n"
            "\n"
            "nlu:\n"
            "{% for generated_intent in ddd_examples %}"
            "{% if generated_intent.samples %}"
            "- intent: {{ ddd }}:{{ generated_intent.name }}\n"
            "  examples: |\n"
            "{% for sample in generated_intent.samples %}"
            "    - {{ sample }}\n"
            "{% endfor %}"
            "\n"
            "{% endif %}"
            "{% endfor %}"
            ""
            "{% for generated_intent in general_examples %}"
            "{% if generated_intent.samples %}"
            "- intent: {{ generated_intent.name }}\n"
            "  examples: |\n"
            "{% for sample in generated_intent.samples %}"
            "    - {{ sample }}\n"
            "{% endfor %}"
            "\n"
            "{% endif %}"
            "{% endfor %}"
            ""
            "{% for synonym_object in synonym_objects %}"
            "- synonym: {{ ddd }}:{{ synonym_object.value }}\n"
            "  examples: |\n"
            "{% for synonym in synonym_object.synonyms %}"
            "    - {{ synonym }}\n"
            "{% endfor %}"
            "\n"
            "{% endfor %}"
            "\n"
            "{% for lookup_object in lookup_objects %}"
            "- lookup: {{ ddd }}.sort.{{ lookup_object.value }}\n"
            "  examples: |\n"
            "{% for lookup_entry in lookup_object.entries %}"
            "    - {{ lookup_entry }}\n"
            "{% endfor %}"
            "\n"
            "{% endfor %}"
        )
        grammar = self._ddd.grammars[self._language_code]
        synonyms = self._entity_synonyms_from_custom_sorts(grammar)
        lookup = self._lookup_table()
        rasa_data = data_template.stream(
            ddd_examples=examples,
            general_examples=self._general_examples(),
            synonym_objects=synonyms,
            lookup_objects=lookup,
            ddd=self._ddd.name
        )

        return rasa_data

    def _general_examples(self):
        yield GeneratedIntent(NEGATIVE_INTENT, list(self._language_examples.negative))
        yield GeneratedBuiltinAnswerIntent(Yes.YES, self._language_examples.yes)
        yield GeneratedBuiltinAnswerIntent(No.NO, self._language_examples.no)
        yield GeneratedBuiltinRequestIntent(TOP, self._language_examples.top)
        yield GeneratedBuiltinRequestIntent(UP, self._language_examples.up)
        yield GeneratedBuiltinRequestIntent(HOW, self._language_examples.how)
        yield GeneratedBuiltinReportIntent(DONE, self._language_examples.done)
        yield GeneratedIntent(
            NEGATIVE_PERCEPTION_ICM.as_semantic_expression(), self._language_examples.negative_perception
        )
        yield GeneratedIntent(
            NEGATIVE_ISSUE_ACCEPTANCE_ICM.as_semantic_expression(), self._language_examples.negative_acceptance
        )
        yield GeneratedIntent(Move.THANK_YOU, self._language_examples.thank_you)
        yield GeneratedIntent(Move.GREET, self._language_examples.greeting)

    def _entity_synonyms_from_custom_sorts(self, grammar):
        def sorted_sorts(sorts):
            return sorted(list(sorts), key=lambda CustomSort: CustomSort.name)

        for sort in sorted_sorts(self._ddd.ontology.get_sorts().values()):
            if sort.is_builtin() or sort.name in self._excluded_sorts:
                continue
            for individual, grammar_entries in self._all_individuals_of_custom_sort(grammar, sort):
                yield self._create_synonym_object(individual, grammar_entries)

    @staticmethod
    def _create_synonym_object(value, synonyms):
        return {
            "value": value,
            "synonyms": synonyms,
        }

    def _lookup_table(self):
        def sorted_sorts(sorts):
            return sorted(list(sorts), key=lambda CustomSort: CustomSort.name)

        for sort in sorted_sorts(self._ddd.ontology.get_sorts().values()):
            if sort.name in self._language_examples.lookup_data:
                lookup_entries = self._language_examples.lookup_data[sort.name]
                yield self._create_lookup_object(sort.name, lookup_entries)

    @staticmethod
    def _create_lookup_object(value, lookup_entries):
        return {
            "value": value,
            "entries": lookup_entries,
        }

    def _create_intent_samples(self, grammar, ddd, intent):
        head = intent.text_chunks[0]
        texts = intent.text_chunks[1:]
        num_samples = self._num_training_instances
        try:
            samples = self._examples_with_individuals(
                grammar, ddd, texts, intent.required_entities, [head], num_samples
            )[:num_samples]
            return samples
        except UnexpectedPropositionalEntityEncounteredException:
            return []

    def _examples_with_individuals(
        self,
        grammar,
        ddd,
        text_chunks,
        required_entities,
        examples_so_far,
        num_examples=1,
        sorts_of_propositional_slots_in_sample=[]
    ):
        if not text_chunks and not required_entities:
            return examples_so_far
        if not sorts_of_propositional_slots_in_sample:
            sorts_of_propositional_slots_in_sample = self._get_all_sorts_of_propositional_slots_in_sample(required_entities)
        tail = text_chunks[0]
        required_entity = required_entities[0]
        all_new_examples = []
        for example in examples_so_far:
            if required_entity.is_sortal:
                new_examples = sorted(
                    list(self._examples_from_sortal_individual(grammar, ddd, required_entity, example,
                                                               tail))[:num_examples]
                )
                all_new_examples.extend(new_examples)
            elif required_entity.is_propositional:
                predicate = self._ddd.ontology.get_predicate(required_entity.name)
                if self._should_be_generated_as_entity(predicate.getSort()):
                    new_examples = sorted(
                        list(
                            self._examples_from_propositional_individual(
                                grammar, ddd, required_entity, example, tail, sorts_of_propositional_slots_in_sample
                            )
                        )[:num_examples]
                    )
                    all_new_examples.extend(new_examples)

                else:
                    message = (
                        f"Expected only sortal slots for built-in sort '{predicate.getSort().get_name()}' "
                        f"but got a propositional slot for predicate '{predicate.get_name()}'. "
                        f"Skipping this training data example."
                    )
                    warnings.warn(message, UserWarning)
                    raise UnexpectedPropositionalEntityEncounteredException(message)

            else:
                raise UnexpectedRequiredEntityException(
                    f"Expected either a sortal or propositional required entity but got a "
                    f"{required_entity.__class__.__name__}"
                )

        return self._examples_with_individuals(
            grammar,
            ddd,
            text_chunks[1:],
            required_entities[1:],
            all_new_examples,
            num_examples=1,
            sorts_of_propositional_slots_in_sample=sorts_of_propositional_slots_in_sample
        )

    def _get_all_sorts_of_propositional_slots_in_sample(self, required_entities):
        predicates_in_sample = (
            self._ddd.ontology.get_predicate(entity.name) for entity in required_entities if entity.is_propositional
        )
        return tuple(predicate.getSort().get_name() for predicate in predicates_in_sample)

    def _examples_from_sortal_individual(self, grammar, ddd, required_sortal_entity, example_so_far, tail):
        sort = self._ddd.ontology.get_sort(required_sortal_entity.name)
        if sort.name in self._excluded_sorts:
            return []
        individuals = self._individual_grammar_entries_samples(grammar, sort)
        shuffle(individuals)
        template = self._entity_template_of_sortal_individual(sort)
        return self._examples_from_individuals(
            template, ddd, individuals, example_so_far, tail, predicate_name=None, sort_name=sort.get_name()
        )

    def _individual_grammar_entries_samples(self, grammar, sort):
        if sort.is_builtin():
            return self._sample_individuals_of_builtin_sort(sort)
        return list(self._all_individual_training_examples_of_custom_sort(grammar, sort))

    def _sample_individuals_of_builtin_sort(self, sort):
        examples = self._language_examples.get_builtin_sort_examples(sort)
        return [[entry] for entry in examples]

    def _examples_from_propositional_individual(
        self, grammar, ddd, required_propositional_entity, example_so_far, tail, sorts_of_propositional_slots_in_sample
    ):
        predicate_name = required_propositional_entity.name
        predicate = self._ddd.ontology.get_predicate(predicate_name)
        sort = predicate.getSort()
        if sort.get_name() in self._excluded_sorts:
            return []
        individuals = self._individual_grammar_entries_samples(grammar, sort)
        if sort.get_name() == STRING:
            predicate_specific_samples = self._string_examples_of_predicate(grammar, predicate)
            individuals.extend([[predicate_specific_sample]
                                for predicate_specific_sample in predicate_specific_samples])
        shuffle(individuals)
        template = self._entity_template_of_propositional_individual(
            sort.name, sorts_of_propositional_slots_in_sample
        )
        return self._examples_from_individuals(
            template, ddd, individuals, example_so_far, tail, predicate_name=predicate_name, sort_name=sort.get_name()
        )

    def _string_examples_of_predicate(self, grammar, predicate):
        return grammar.strings_of_predicate(predicate.get_name())

    def _examples_from_individuals(
        self, template, ddd, individuals_grammar_entries, example_so_far, tail, predicate_name, sort_name
    ):
        for grammar_entries in individuals_grammar_entries:
            for grammar_entry in grammar_entries:
                entity = template.render(
                    grammar_entry=grammar_entry, ddd=ddd, predicate_name=predicate_name, sort_name=sort_name
                )
                example = self._extend_example(entity, example_so_far, tail)
                yield example

    @staticmethod
    def _extend_example(entity, example_so_far, tail=None):
        head = example_so_far
        tail = tail or ""
        return "".join([head, entity, tail])

    def _create_sortal_answer_samples(self, grammar, ddd, sort, intent_templates):
        def make_random_sample(examples):
            try:
                return sample(examples, self._num_training_instances)
            except ValueError:
                return examples

        def yield_examples(grammar_entries):
            examples = self._examples_of_individual(
                grammar_entries, ddd, sort.get_name(), intent_templates,
                self._entity_template_of_sortal_individual(sort)
            )
            for example in examples:
                yield example

        if self.there_is_lookup_table_contents_for_sort(sort):
            lookup_table_data = self._language_examples.lookup_data[sort.name]
            samples_from_lookup_table = make_random_sample(lookup_table_data)
            for lookup_examples in samples_from_lookup_table:
                for example in yield_examples([lookup_examples]):
                    yield example
        else:
            for grammar_entries in self._individual_grammar_entries_samples(grammar, sort):
                for example in yield_examples(grammar_entries):
                    yield example

    def _should_be_generated_as_entity(self, sort):
        return sort.is_string_sort() or sort.is_person_name_sort() or not sort.is_builtin()

    def _entity_template_of_sortal_individual(self, sort):
        if self._should_be_generated_as_entity(sort):
            return self._entity_template_without_role
        return self._builtin_entity_template

    def _entity_template_of_propositional_individual(self, sort_name, sorts_of_propositional_slots_in_sample):
        if sorts_of_propositional_slots_in_sample.count(sort_name) > 1:
            return self._entity_template_with_role
        return self._entity_template_without_role

    def _examples_of_individual(self, grammar_entries, ddd, identifier, intent_templates, entity_template):
        for grammar_entry in grammar_entries:
            examples = self._examples_from_templates(grammar_entry, ddd, identifier, intent_templates, entity_template)
            for example in examples:
                yield example

    def _examples_from_templates(self, grammar_entry, ddd, identifier, intent_templates, entity_template):
        for intent_template in intent_templates:
            entity = entity_template.render(grammar_entry=grammar_entry, ddd=ddd, sort_name=identifier)
            yield intent_template.render(name=entity)
