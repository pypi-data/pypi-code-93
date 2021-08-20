from django.urls import path

from lfl_admin.competitions.views import match_stats

urlpatterns = [

    path('Match_stats/Fetch/', match_stats.Match_stats_Fetch),
    path('Match_stats/Add', match_stats.Match_stats_Add),
    path('Match_stats/Update', match_stats.Match_stats_Update),
    path('Match_stats/Remove', match_stats.Match_stats_Remove),
    path('Match_stats/Lookup/', match_stats.Match_stats_Lookup),
    path('Match_stats/Info/', match_stats.Match_stats_Info),
    path('Match_stats/Copy', match_stats.Match_stats_Copy),

]
