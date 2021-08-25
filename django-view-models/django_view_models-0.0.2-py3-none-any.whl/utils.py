from django.apps import apps

from .models import ViewModel, MaterializedViewModel

def create_views():
    for m in apps.get_models() :
        if issubclass(m, ViewModel) :
            m.create_view()
def refresh_views():
    for m in apps.get_models() :
        if issubclass(m, MaterializedViewModel) :
            m.refresh_view()
def sync_views():
    create_views()
    refresh_views()