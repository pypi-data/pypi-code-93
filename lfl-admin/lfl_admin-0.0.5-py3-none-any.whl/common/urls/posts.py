from django.urls import path

from lfl_admin.common.views import posts

urlpatterns = [

    path('Posts/Fetch/', posts.Posts_Fetch),
    path('Posts/Add', posts.Posts_Add),
    path('Posts/Update', posts.Posts_Update),
    path('Posts/Remove', posts.Posts_Remove),
    path('Posts/Lookup/', posts.Posts_Lookup),
    path('Posts/Info/', posts.Posts_Info),
    path('Posts/Copy', posts.Posts_Copy),

]
