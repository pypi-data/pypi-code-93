import uuid

from django.utils.text import slugify

from .settings import (
    ENABLE_FUZZY_SEARCH,
    FUZZY_SEARCH_PERCENTAGE,
    SEARCH_WORD_BY_WORD_KEYWORDS,
)


if ENABLE_FUZZY_SEARCH:
    try:
        # use fuzzy search, keep setting to True
        from fuzzywuzzy import fuzz
    except ImportError:
        # can't find package, set setting to False and print error
        print(
            "WARNING: Var DJANGOCMS_FAQ_ENABLE_FUZZY_SEARCH is set to True in your project's settings, but your installation of Python can't find the package fuzzywuzzy.\nHave you tried to install the package using \"python3 -m pip install djangocms_faq[fuzzy_search]\"?\nNot using fuzzy search for this time..."
        )
        ENABLE_FUZZY_SEARCH = False


from djangocms_faq.models import FaqPluginModel, QuestionFaqPluginModel


def get_answers(query, search_in, draft):

    if not len(query):
        return

    query = slugify(query)  # replace "AuJoürd'hui" by "aujourd-hui"

    if ENABLE_FUZZY_SEARCH:
        query = query.replace("-", " ")  # replace "AuJoürd'hui" by "aujourd hui"

    answers_questions = []
    answers_keywords = []

    uuid_list = [uuid.UUID(faq_uuid) for faq_uuid in search_in.split()]

    faq_list = [
        faq.id
        for faq in FaqPluginModel.objects.exclude(
            placeholder__page__publisher_is_draft=bool(draft)
        ).filter(uuid__in=uuid_list)
    ]

    # get questions
    questions = QuestionFaqPluginModel.objects.exclude(
        placeholder__page__publisher_is_draft=bool(draft)
    ).filter(parent__id__in=faq_list)

    # go through every question in list of selected FAQs
    for question in questions:

        # search in question title
        # fuzzy search = handle some user mistakes
        if ENABLE_FUZZY_SEARCH:
            question_str = slugify(question.question).replace("-", " ")

            # debug stuff:
            # print(query + " - " + question_str + " =>", end="")
            # print((30 - (len(query + " - " + question_str))) * " " + str(fuzz.token_sort_ratio(query, question_str)))

            # query is the slugified user query
            # question_str is the slugified question text
            if (
                fuzz.token_sort_ratio(query, question_str)
                >= FUZZY_SEARCH_PERCENTAGE  # see https://github.com/seatgeek/fuzzywuzzy#token-sort-ratio
            ) or (query in question_str):
                answers_questions.append(question)
        else:
            if query in slugify(question.question):
                answers_questions.append(question)

        # search in keywords
        for keyword in question.keywords.all():
            if ENABLE_FUZZY_SEARCH:
                keyword = slugify(keyword).replace("-", " ")
                # debug stuff
                # print("  " + query + " - " + keyword + " =>", end="")
                # print((30 - (len(query + " - " + keyword))) * " " + str(fuzz.token_sort_ratio(query, keyword)))

                # query is the slugified user query
                # keyword is the slugified keyword
                if fuzz.token_sort_ratio(query, keyword) >= FUZZY_SEARCH_PERCENTAGE:
                    answers_keywords.append(question)
            else:
                if query in slugify(keyword):
                    answers_keywords.append(question)

            # search correspondance word by word for each word in query and slugs
            if SEARCH_WORD_BY_WORD_KEYWORDS:
                query_list = query.split(" ")
                for query_word in query_list:
                    for keyword_word in keyword.split(" "):
                        if ENABLE_FUZZY_SEARCH:
                            if (
                                fuzz.token_sort_ratio(query_word, keyword_word)
                                >= FUZZY_SEARCH_PERCENTAGE
                            ):
                                answers_keywords.append(question)
                        else:
                            if query_word == keyword_word:
                                answers_keywords.append(question)

    # all answers
    answers = answers_questions + answers_keywords

    # get unique values
    answers = list(set(answers))

    return answers
