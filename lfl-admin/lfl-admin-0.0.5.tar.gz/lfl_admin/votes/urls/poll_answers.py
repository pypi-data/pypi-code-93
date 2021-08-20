from django.urls import path

from lfl_admin.votes.views import poll_answers

urlpatterns = [

    path('Poll_answers/Fetch/', poll_answers.Poll_answers_Fetch),
    path('Poll_answers/Add', poll_answers.Poll_answers_Add),
    path('Poll_answers/Update', poll_answers.Poll_answers_Update),
    path('Poll_answers/Remove', poll_answers.Poll_answers_Remove),
    path('Poll_answers/Lookup/', poll_answers.Poll_answers_Lookup),
    path('Poll_answers/Info/', poll_answers.Poll_answers_Info),
    path('Poll_answers/Copy', poll_answers.Poll_answers_Copy),

]
