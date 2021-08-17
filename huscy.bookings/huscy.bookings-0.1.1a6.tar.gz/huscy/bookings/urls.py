from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter

from huscy.bookings import views
from huscy.projects.urls import project_router

router = DefaultRouter()
router.register('timeslots', views.TimeslotViewSet)

project_router.register('timeslots', views.ListTimeslotsViewSet, basename='project-timeslots')

experiment_router = NestedDefaultRouter(project_router, 'experiments', lookup='experiment')
experiment_router.register('timeslots', views.ListTimeslotsViewSet, basename='experiment-timeslots')

urlpatterns = [
]

urlpatterns += router.urls
urlpatterns += project_router.urls
urlpatterns += experiment_router.urls
