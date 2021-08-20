from django.urls import path

from lfl_admin.constructions.views import stadium_rating

urlpatterns = [

    path('Stadium_rating/Fetch/', stadium_rating.Stadium_rating_Fetch),
    path('Stadium_rating/Add', stadium_rating.Stadium_rating_Add),
    path('Stadium_rating/Update', stadium_rating.Stadium_rating_Update),
    path('Stadium_rating/Remove', stadium_rating.Stadium_rating_Remove),
    path('Stadium_rating/Lookup/', stadium_rating.Stadium_rating_Lookup),
    path('Stadium_rating/Info/', stadium_rating.Stadium_rating_Info),
    path('Stadium_rating/Copy', stadium_rating.Stadium_rating_Copy),

]
