from django.urls import path

from lfl_admin.votes.views import poll_votes

urlpatterns = [

    path('Poll_votes/Fetch/', poll_votes.Poll_votes_Fetch),
    path('Poll_votes/Add', poll_votes.Poll_votes_Add),
    path('Poll_votes/Update', poll_votes.Poll_votes_Update),
    path('Poll_votes/Remove', poll_votes.Poll_votes_Remove),
    path('Poll_votes/Lookup/', poll_votes.Poll_votes_Lookup),
    path('Poll_votes/Info/', poll_votes.Poll_votes_Info),
    path('Poll_votes/Copy', poll_votes.Poll_votes_Copy),

]
