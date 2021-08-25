import warnings

from tala.model.grammar.intent import Question, Request, Answer, UserReport
from tala.model.grammar.required_entity import RequiredPropositionalEntity, RequiredSortalEntity
from tala.model.sort import STRING
from tala.nl.gf import rgl_grammar_entry_types
from tala.nl.gf.grammar_entry_types import Constants
from tala.nl import selection_policy_names
from tala.utils.as_json import AsJSONMixin


class NoIndividualsFoundException(Exception):
    pass


class NoRequestsFoundException(Exception):
    pass


class NoQuestionsFoundException(Exception):
    pass


class UnexpectedIndividualsFoundException(Exception):
    pass


class UnexpectedRequestsFoundException(Exception):
    pass


class UnexpectedQuestionsFoundException(Exception):
    pass


class UnexpectedAnswersFoundException(Exception):
    pass


class UnexpectedAnswerFormatException(Exception):
    pass


class UnexpectedStringsFoundException(Exception):
    pass


class GrammarBase(AsJSONMixin):
    def __init__(self, grammar_root, grammar_path):
        super(GrammarBase, self).__init__()
        self._grammar_root = grammar_root
        self._grammar_path = grammar_path
        self._local_individual_identifier = None

    def as_dict(self):
        return {
            "answers": self.answers(),
        }

    def requests_of_action(self, action):
        raise NotImplementedError(f"{self.__class__.__name__}.requests_of_action(...) need to be implemented.")

    def user_reports_of_action(self, action):
        raise NotImplementedError(f"{self.__class__.__name__}.user_reports_of_action(...) need to be implemented.")

    def _find_individuals_of(self, name):
        raise NotImplementedError(f"{self.__class__.__name__}._find_individual(...) need to be implemented.")

    def entries_of_individual(self, name):
        individuals = self._find_individuals_of(name)
        if len(individuals) < 1:
            all_names = [individual.get("name") for individual in self._grammar_root.findall(Constants.INDIVIDUAL)]
            raise NoIndividualsFoundException(
                f"Expected at least one <{Constants.INDIVIDUAL} ...> for individual '{name}', "
                f"but it was not found among {all_names} in {self._grammar_path}"
            )
        if len(individuals) > 1:
            raise UnexpectedIndividualsFoundException(
                f"Expected a single <{Constants.INDIVIDUAL} ...> for individual '{name}' "
                f"but found {len(individuals):d} in {self._grammar_path}"
            )
        return self._process_individual_entries(individuals[0])

    def _process_individual_entries(self, individual_element):
        if self._element_has_children(individual_element):
            return self._get_item_contents_for_individual_element(individual_element)
        else:
            return [individual_element.text.strip()]

    def _element_has_children(self, element):
        return len(list(element)) != 0

    def _get_item_contents_for_individual_element(self, element):
        one_of = element.find("one-of")
        return [e.text.strip() for e in list(one_of.iter(tag="item"))]

    def questions_of_predicate(self, predicate):
        questions = self._grammar_root.findall(f"question[@predicate='{predicate}'][@speaker='user']")
        if len(questions) < 1:
            actual_questions = self._grammar_root.findall("question[@speaker='user']")
            actual_predicates = [question.get("predicate") for question in actual_questions]
            raise NoQuestionsFoundException(
                f"Expected at least one <question speaker='user'...> for predicate '{predicate}' "
                f"but it was not found among {actual_predicates} in {self._grammar_path}"
            )
        if len(questions) > 1:
            raise UnexpectedQuestionsFoundException(
                f"Expected a single <question speaker='user' ...> for predicate '{predicate}' "
                f"but found {len(questions):d} in {self._grammar_path}"
            )
        question = questions[0]
        items = self._plain_text_items_of(question)
        for item in items:
            text_chunks, required_entities = self._chunks_and_entities_of_item(item)
            yield Question(predicate, text_chunks, required_entities)

    def answers(self):
        answers = self._grammar_root.findall("answer[@speaker='user']")
        if not answers:
            return
        if len(answers) > 1:
            raise UnexpectedAnswersFoundException(
                f"Expected a single <answer speaker='user'> but found {len(answers):d} in {self._grammar_path}"
            )
        answer = answers[0]
        items = self._plain_text_items_of(answer)
        for item in items:
            text_chunks, required_entities = self._chunks_and_entities_of_item(item)
            if not required_entities:
                raise UnexpectedAnswerFormatException(
                    f"Expected at least one <{self._local_individual_identifier} .../> in every item in "
                    f"<answer speaker=\"user\"> but found some without"
                )
            yield Answer(text_chunks, required_entities)

    def strings_of_predicate(self, predicate):
        strings = self._grammar_root.findall(f"string[@predicate='{predicate}']")
        if len(strings) > 1:
            raise UnexpectedStringsFoundException(
                f"Expected a single <string predicate='{predicate}'> but found {len(strings):d} in {self._grammar_path}"
            )

        if len(strings) == 0:
            warnings.warn(
                f"Expected training examples for predicate '{predicate}' of sort '{STRING}' but found none. "
                f"Add them with:\n"
                f"\n"
                f"<string predicate=\"{predicate}\">\n"
                f"  <one-of>\n"
                f"    <item>an example</item>\n"
                f"    <item>another example</item>\n"
                f"  </one-of>\n"
                f"</string>"
            )
            return

        string = strings[0]
        items = self._plain_text_items_of(string)
        for item in items:
            text_chunks, required_entities = self._chunks_and_entities_of_item(item)
            if any(required_entities):
                raise UnexpectedIndividualsFoundException(
                    f"Expected no <{self._local_individual_identifier} ...> in <string predicate='{predicate}'> "
                    f"but found some"
                )
            assert len(text_chunks) == 1, f"Expected 1 text chunk but got {len(text_chunks):d}"
            yield text_chunks[0]

    def _chunks_and_entities_of_item(self, item):
        text_chunks = [item.text or ""]
        required_entities = []
        local_individuals = item.findall(self._local_individual_identifier)
        for individual_element in local_individuals:
            required_entity = self._required_entity_from_individual_element(individual_element)
            required_entities.append(required_entity)
            tail = individual_element.tail or ""
            text_chunks.append(tail)
        self._strip_chunks(text_chunks)
        return text_chunks, required_entities

    def _strip_chunks(self, chunks):
        chunks[0] = chunks[0].lstrip()
        chunks[-1] = chunks[-1].rstrip()

    def _required_entity_from_individual_element(self, element):
        predicate = element.attrib.get("predicate")
        if predicate:
            return RequiredPropositionalEntity(predicate)
        sort = element.attrib.get("sort")
        if sort:
            return RequiredSortalEntity(sort)
        raise UnexpectedIndividualsFoundException(
            f"Expected either a 'sort' or 'predicate' attribute in <{self._local_individual_identifier} ...>: {element}"
        )

    def _plain_text_items_of(self, item):
        raise NotImplementedError(f"{self.__class__.__name__}._plain_text_items_of(...) need to be implemented.")

    def selection_policy_of_report(self, action, status):
        return selection_policy_names.DISABLED


class Grammar(GrammarBase):
    def __init__(self, language_code, grammar_path):
        super(Grammar, self).__init__(language_code, grammar_path)
        self._local_individual_identifier = Constants.SLOT

    def requests_of_action(self, name):
        actions = self._grammar_root.findall(f"{Constants.ACTION}[@name='{name}']")
        if len(actions) < 1:
            all_actions = self._grammar_root.findall(Constants.ACTION)
            all_names = [action.get("name") for action in all_actions]
            raise NoRequestsFoundException(
                f"Expected at least one <action ...> for action '{name}' "
                f"but it was not found among {all_names} in {self._grammar_path}"
            )
        if len(actions) > 1:
            raise UnexpectedRequestsFoundException(
                f"Expected a single <action ...> for action '{name}' but found {len(actions):d} in {self._grammar_path}"
            )
        action_item = actions[0]
        items = list(self._plain_text_items_of(action_item))
        for item in items:
            text_chunks, required_entities = self._chunks_and_entities_of_item(item)
            yield Request(name, text_chunks, required_entities)

    def user_reports_of_action(self, action_name):
        reports = self._grammar_root.findall(
            f"{Constants.REPORT}[@speaker='user'][@action='{action_name}'][@status='done']"
        )
        if len(reports) == 0:
            return
        report = reports[0]
        items = list(self._plain_text_items_of(report))
        for item in items:
            text_chunks, required_entities = self._chunks_and_entities_of_item(item)
            yield UserReport(action_name, text_chunks, required_entities)

    def _plain_text_items_of(self, root):
        def get_items(root):
            items = self._items_of(root)
            for item in items:
                if item.find(Constants.VP) is not None or item.find(Constants.NP) is not None:
                    continue
                yield item

        plain_text_items = list(get_items(root))
        if not plain_text_items:
            warnings.warn(
                f"{self.__class__.__name__} ignores element '{root.tag}' with attributes {root.attrib} "
                f"since there are no plain text items"
            )
        return plain_text_items

    def _items_of(self, root):
        items = root.findall(f"./{Constants.ONE_OF}/{Constants.ITEM}")
        if not items:
            yield root
        for item in items:
            yield item

    def _find_individuals_of(self, name):
        return self._grammar_root.findall(f"{Constants.INDIVIDUAL}[@name='{name}']")

    def selection_policy_of_report(self, action, status):
        report_element = self._grammar_root.find(f"report[@action='{action}'][@status='{status}']")
        if report_element is not None:
            one_of_element = report_element.find(Constants.ONE_OF)
            if one_of_element is not None and Constants.SELECTION in one_of_element.attrib:
                return one_of_element.attrib[Constants.SELECTION]
        return super(Grammar, self).selection_policy_of_report(action, status)


class GrammarForRGL(GrammarBase):
    def __init__(self, grammar_root, grammar_path):
        super(GrammarForRGL, self).__init__(grammar_root, grammar_path)
        self._local_individual_identifier = Constants.INDIVIDUAL

    def requests_of_action(self, action):
        requests = self._grammar_root.findall(f"{rgl_grammar_entry_types.REQUEST}[@action='{action}']")
        if len(requests) < 1:
            actual_requests = self._grammar_root.findall(rgl_grammar_entry_types.REQUEST)
            actual_actions = [request.get("action") for request in actual_requests]
            raise NoRequestsFoundException(
                f"Expected at least one <request ...> for action '{action}' "
                f"but it was not found among {actual_actions} in {self._grammar_path}"
            )
        if len(requests) > 1:
            raise UnexpectedRequestsFoundException(
                f"Expected a single <request ...> for action '{action}' "
                f"but found {len(requests):d} in {self._grammar_path}"
            )
        request = requests[0]
        items = self._plain_text_items_of(request)
        for item in items:
            text_chunks, required_entities = self._chunks_and_entities_of_item(item)
            yield Request(action, text_chunks, required_entities)

    def _plain_text_items_of(self, item):
        utterances = item.findall(rgl_grammar_entry_types.UTTERANCE)
        if not utterances:
            warnings.warn(
                f"{self.__class__.__name__} ignores element '{item.tag}' with attributes {item.attrib} "
                f"since it has no <utterance>"
            )
            return

        for utterance in utterances:
            items = utterance.findall(f"./{Constants.ONE_OF}/{Constants.ITEM}")
            if not items:
                yield utterance
            for item in items:
                yield item

    def _find_individuals_of(self, name):
        return self._grammar_root.findall(
            f"{Constants.INDIVIDUAL}[@name='{name}']/{rgl_grammar_entry_types.PROPER_NOUN}"
        )
