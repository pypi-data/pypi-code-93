from django.urls import path

from lfl_admin.competitions.views import referee_category

urlpatterns = [

    path('Referee_category/Fetch/', referee_category.Referee_category_Fetch),
    path('Referee_category/Add', referee_category.Referee_category_Add),
    path('Referee_category/Update', referee_category.Referee_category_Update),
    path('Referee_category/Remove', referee_category.Referee_category_Remove),
    path('Referee_category/Lookup/', referee_category.Referee_category_Lookup),
    path('Referee_category/Info/', referee_category.Referee_category_Info),
    path('Referee_category/Copy', referee_category.Referee_category_Copy),

]
