from django.urls import path

from lfl_admin.votes.views import polls

urlpatterns = [

    path('Polls/Fetch/', polls.Polls_Fetch),
    path('Polls/Add', polls.Polls_Add),
    path('Polls/Update', polls.Polls_Update),
    path('Polls/Remove', polls.Polls_Remove),
    path('Polls/Lookup/', polls.Polls_Lookup),
    path('Polls/Info/', polls.Polls_Info),
    path('Polls/Copy', polls.Polls_Copy),

]
