from django.urls import path

from lfl_admin.competitions.views import match_resaults

urlpatterns = [

    path('Match_resaults/Fetch/', match_resaults.Match_resaults_Fetch),
    path('Match_resaults/Add', match_resaults.Match_resaults_Add),
    path('Match_resaults/Update', match_resaults.Match_resaults_Update),
    path('Match_resaults/Remove', match_resaults.Match_resaults_Remove),
    path('Match_resaults/Lookup/', match_resaults.Match_resaults_Lookup),
    path('Match_resaults/Info/', match_resaults.Match_resaults_Info),
    path('Match_resaults/Copy', match_resaults.Match_resaults_Copy),

]
