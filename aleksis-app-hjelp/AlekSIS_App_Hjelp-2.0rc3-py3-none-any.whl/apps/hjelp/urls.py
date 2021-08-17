from django.urls import path

from . import views

urlpatterns = [
    path("issues/report/", views.report_issue, name="report_issue"),
    path("feedback/", views.feedback, name="feedback"),
    path("faq/", views.faq, name="faq"),
    path("faq/ask/", views.ask_faq, name="ask_faq"),
    path("faq/order/", views.OrderFAQ.as_view(), name="order_faq"),
    path("faq/section/create/", views.CreateFAQSection.as_view(), name="create_faq_section"),
    path("faq/section/<pk>/delete/", views.DeleteFAQSection.as_view(), name="delete_faq_section"),
    path("faq/question/create/", views.CreateFAQQuestion.as_view(), name="create_faq_question"),
    path(
        "faq/question/<pk>/update/", views.UpdateFAQQuestion.as_view(), name="update_faq_question"
    ),
    path(
        "faq/question/<pk>/delete/", views.DeleteFAQQuestion.as_view(), name="delete_faq_question"
    ),
    path(
        "issues/get_next_properties/",
        views.issues_get_next_properties,
        name="issues_get_next_properties",
    ),
]
