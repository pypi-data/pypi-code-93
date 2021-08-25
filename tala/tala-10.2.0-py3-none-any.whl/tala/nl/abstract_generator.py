import os
import warnings

from tala.ddd.grammar.reader import GrammarReader
from tala.model.grammar.intent import Answer, AnswerNegation
from tala.model.grammar.required_entity import RequiredSortalEntity
from tala.nl.examples import Examples
from tala.nl.generated_intent import GeneratedCustomIntent
from tala.nl.constants import ANSWER_INTENT, ANSWER_NEGATION_INTENT
import tala


class GrammarFormatNotSupportedException(Exception):
    pass


class UnexpectedPropositionalEntityEncounteredException(Exception):
    pass


class UnexpectedRequiredEntityException(Exception):
    pass


class AbstractGenerator(object):
    def __init__(
        self,
        ddd,
        grammar_path,
        language_code,
        custom_entity_examples_for_builtin_sorts={},
        lookup_table_contents_for_sorts={},
        excluded_sorts=set()
    ):
        self._ddd = ddd
        self._grammar_path = grammar_path
        self._language_code = language_code
        self._language_examples = Examples.from_language(
            language_code, custom_entity_examples_for_builtin_sorts, lookup_table_contents_for_sorts
        )
        self._excluded_sorts = set(excluded_sorts)

    def stream(self, file_object):
        raise NotImplementedError()

    def generate(self):
        raise NotImplementedError()

    def _create_intent_samples(self, grammar, ddd, intent):
        raise NotImplementedError()

    def _create_sortal_answer_samples(self, grammar, ddd, sort, intent_templates):
        raise NotImplementedError()

    def _format_action(self, name):
        raise NotImplementedError()

    def _format_question(self, name):
        raise NotImplementedError()

    def _generate_examples(self):
        if not GrammarReader.xml_grammar_exists_for_language(self._language_code, self._grammar_path):
            raise GrammarFormatNotSupportedException(
                "Expected an XML-based grammar at '%s', but it does not exist" %
                os.path.abspath(GrammarReader.path(self._language_code, self._grammar_path))
            )

        grammar = self._ddd.grammars[self._language_code]
        ddd = self._ddd.name

        intent_generators = [
            self._examples_of_actions(grammar, ddd),
            self._examples_of_questions(grammar, ddd),
            self._examples_of_answers(grammar, ddd),
            self._examples_of_answer_negations(grammar, ddd),
            self._examples_of_user_reports(grammar, ddd)
        ]

        for generated_intents in intent_generators:
            for generated_intent in generated_intents:
                yield generated_intent

    def _examples_of_actions(self, grammar, ddd):
        for action in sorted(self._ddd.ontology.get_ddd_specific_actions()):
            yield self._generated_action_intent_for(grammar, ddd, action)

    def _generated_action_intent_for(self, grammar, ddd, action):
        def samples(requests):
            for request in requests:
                for sample in self._create_intent_samples(grammar, ddd, request):
                    yield sample

        intent = self._format_action(action)
        try:
            requests = list(grammar.requests_of_action(action))
        except tala.model.grammar.grammar.NoRequestsFoundException:
            warnings.warn(f"Grammar contains no entries for action '{action}', so training data will not be generated.")
            requests = []
        if len(requests) == 1:
            warnings.warn(f"Grammar contains one entry for action '{action}', so training data will not be generated.")
            requests = []
        return GeneratedCustomIntent(intent, requests, list(samples(requests)))

    def _examples_of_questions(self, grammar, ddd):
        for resolve_goal in self._ddd.domain.get_all_resolve_goals():
            question = resolve_goal.get_question()
            yield self._generated_question_intent_for(grammar, ddd, question)

    def _generated_question_intent_for(self, grammar, ddd, question):
        def samples(questions):
            for question in questions:
                for sample in self._create_intent_samples(grammar, ddd, question):
                    yield sample

        predicate = question.get_predicate().get_name()
        intent = self._format_question(predicate)
        questions = list(grammar.questions_of_predicate(predicate))
        return GeneratedCustomIntent(intent, questions, list(samples(questions)))

    def _get_sorts_not_in_excluded_sorts(self):
        for sort in self._ddd.ontology.predicate_sorts:
            if sort.get_name() not in self._excluded_sorts:
                yield sort

    def _examples_of_answers(self, grammar, ddd):
        def samples_from_sorts(sorts):
            for sort in sorts:
                templates = list(self._language_examples.answer_templates)
                for sample in self._create_sortal_answer_samples(grammar, ddd, sort, templates):
                    yield sample

        def samples_from_explicit_answers(answers):
            for answer in answers:
                for sample in self._create_intent_samples(grammar, ddd, answer):
                    yield sample

        def answers_from_sorts(sorts):
            for sort in sorts:
                yield Answer(["", ""], [RequiredSortalEntity(sort.get_name())])

        def add_yes_no_to_some_samples(samples):
            yes_samples = [self._language_examples.yes_strict + " " + sample for sample in samples[0::10]]
            no_samples = [self._language_examples.no_strict + " " + sample for sample in samples[1::10]]
            return samples + yes_samples + no_samples

        sorts = [sort for sort in self._get_sorts_not_in_excluded_sorts()]
        explicit_answers = list(grammar.answers())
        answers = list(answers_from_sorts(sorts)) + explicit_answers
        samples = list(samples_from_sorts(sorts)) + list(samples_from_explicit_answers(explicit_answers))
        yes_no_samples = add_yes_no_to_some_samples(samples)
        yield GeneratedCustomIntent(ANSWER_INTENT, answers, yes_no_samples)

    def _examples_of_answer_negations(self, grammar, ddd):
        def generate_samples(sorts):
            for sort in sorts:
                templates = list(self._language_examples.answer_negation_templates)
                for sample in self._create_sortal_answer_samples(grammar, ddd, sort, templates):
                    yield sample

        def answers_from_sorts(sorts):
            for sort in sorts:
                yield AnswerNegation(["", ""], [RequiredSortalEntity(sort.get_name())])

        sorts = [sort for sort in self._get_sorts_not_in_excluded_sorts() if not sort.is_string_sort()]
        answers = list(answers_from_sorts(sorts))
        samples = list(generate_samples(sorts))
        yield GeneratedCustomIntent(ANSWER_NEGATION_INTENT, answers, samples)

    def _all_individual_training_examples_of_custom_sort(self, grammar, sort):
        if self.there_is_lookup_table_contents_for_sort(sort):
            return self._all_individual_training_examples_from_lookup_data(sort)
        if self.there_is_entity_examples_contents_for_sort(sort):
            return self._all_individual_training_examples_from_entity_examples(sort)
        return self._all_individual_grammar_entries_of_custom_sort(grammar, sort)

    def there_is_lookup_table_contents_for_sort(self, sort):
        return sort.name in self._language_examples.lookup_data

    def _all_individual_training_examples_from_lookup_data(self, sort):
        return [[entry] for entry in self._language_examples.lookup_data[sort.name]]

    def there_is_entity_examples_contents_for_sort(self, sort):
        return sort.name in self._language_examples.custom_sort_entity_examples

    def _all_individual_training_examples_from_entity_examples(self, sort):
        return [[entry] for entry in self._language_examples.custom_sort_entity_examples[sort.name]]

    def _all_individual_grammar_entries_of_custom_sort(self, grammar, sort):
        individuals = self._ddd.ontology.get_individuals_of_sort(sort.name)
        for individual in individuals:
            yield grammar.entries_of_individual(individual)

    def _all_individuals_of_custom_sort(self, grammar, sort):
        individuals = self._ddd.ontology.get_individuals_of_sort(sort.name)
        for individual in individuals:
            yield individual, grammar.entries_of_individual(individual)

    def _examples_of_user_reports(self, grammar, ddd):
        for action in sorted(self._ddd.domain.get_names_of_user_targeted_actions()):
            yield self._generated_user_report_intent_for(grammar, ddd, action)

    def _generated_user_report_intent_for(self, grammar, ddd, action):
        def samples(reports):
            for report in reports:
                for sample in self._create_intent_samples(grammar, ddd, report):
                    yield sample

        intent = self._format_user_report(action)
        user_reports = list(grammar.user_reports_of_action(action))
        return GeneratedCustomIntent(intent, user_reports, list(samples(user_reports)))
