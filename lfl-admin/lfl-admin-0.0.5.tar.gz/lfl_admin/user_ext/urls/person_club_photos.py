from django.urls import path

from lfl_admin.user_ext.views import person_club_photos

urlpatterns = [

    path('Person_club_photos/Fetch/', person_club_photos.Person_club_photos_Fetch),
    path('Person_club_photos/Add', person_club_photos.Person_club_photos_Add),
    path('Person_club_photos/Update', person_club_photos.Person_club_photos_Update),
    path('Person_club_photos/Remove', person_club_photos.Person_club_photos_Remove),
    path('Person_club_photos/Lookup/', person_club_photos.Person_club_photos_Lookup),
    path('Person_club_photos/Info/', person_club_photos.Person_club_photos_Info),
    path('Person_club_photos/Copy', person_club_photos.Person_club_photos_Copy),

]
