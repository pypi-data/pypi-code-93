from json import dumps

from django.http import HttpResponse

from djangocms_faq.utils import get_answers

from .settings import MAX_QUERY_LENGTH


def AnswerView(request):
    if "question" in request.GET and len(request.GET["question"]) > 2:
        question = request.GET["question"][:MAX_QUERY_LENGTH]

        if "search_in" in request.GET:
            search_in = request.GET["search_in"]
        else:
            search_in = ""

        draft = request.GET.get("draft", False)

        answers = get_answers(question, search_in, draft)

        jsondata = []

        if answers:
            for answer in answers:
                # look mom I'm creating ugly json!
                jsondata.append(
                    {
                        "question": answer.question,
                        "slug": answer.slug,
                        "url": answer.get_full_url,
                        "keywords": [
                            keyword.keyword for keyword in answer.keywords.all()
                        ],
                    }
                )

        return HttpResponse(dumps(jsondata), content_type="application/json")

    return HttpResponse("{}", content_type="application/json")
