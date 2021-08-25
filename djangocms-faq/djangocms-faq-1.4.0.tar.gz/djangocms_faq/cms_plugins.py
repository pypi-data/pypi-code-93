from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import ugettext as _

from djangocms_faq.models import (
    FaqPluginModel,
    QuestionFaqPluginModel,
    SearchFaqPluginModel,
)

from .settings import (
    ANSWER_PLUGINS,
    ENABLE_API,
    MAX_QUERY_LENGTH,
    SHOW_KEYWORDS_ANSWER,
    SHOW_KEYWORDS_QUESTION,
)


@plugin_pool.register_plugin
class FaqPluginPublisher(CMSPluginBase):
    module = _("Faq")
    name = _("Faq Container")
    model = FaqPluginModel
    render_template = "faq/faq_plugin.html"
    allow_children = True
    child_classes = ["FaqPluginQuestionPublisher"]

    def render(self, context, instance, placeholder):
        context.update({"instance": instance})
        return context


@plugin_pool.register_plugin
class FaqPluginQuestionPublisher(CMSPluginBase):
    module = _("Faq")
    name = _("Faq Question")
    model = QuestionFaqPluginModel
    render_template = "faq/faq_question.html"
    allow_children = True
    child_classes = ANSWER_PLUGINS
    parent_classes = ["FaqPluginPublisher"]

    def render(self, context, instance, placeholder):
        context.update({"instance": instance})
        context.update({"show_keywords_question": SHOW_KEYWORDS_QUESTION})
        context.update({"show_keywords_answer": SHOW_KEYWORDS_ANSWER})
        return context


if ENABLE_API:

    from djangocms_faq.utils import get_answers

    @plugin_pool.register_plugin
    class FaqPluginSearchPublisher(CMSPluginBase):
        module = _("Faq")
        name = _("Faq Search")
        model = SearchFaqPluginModel
        render_template = "faq/faq_search.html"
        cache = False

        def render(self, context, instance, placeholder):
            context.update({"instance": instance})
            context.update({"show_keywords_question": SHOW_KEYWORDS_QUESTION})
            context.update({"show_keywords_answer": SHOW_KEYWORDS_ANSWER})

            if (
                "question" in context["request"].GET
                and len(context["request"].GET["question"]) > 2
            ):
                question = context["request"].GET["question"][:MAX_QUERY_LENGTH]

                if "search_in" in context["request"].GET:
                    search_in = context["request"].GET["search_in"]
                else:
                    search_in = ""

                draft = context["request"].GET.get("draft", False)

                context.update({"answers": get_answers(question, search_in, draft)})
            return context
