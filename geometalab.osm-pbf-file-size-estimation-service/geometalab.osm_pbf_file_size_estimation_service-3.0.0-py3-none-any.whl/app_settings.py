import os
from django.conf import settings


PBF_FILE_SIZE_ESTIMATION_CSV_FILE_PATH = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'planet-stats.csv')
if hasattr(settings, 'PBF_FILE_SIZE_ESTIMATION_CSV_FILE_PATH'):
    PBF_FILE_SIZE_ESTIMATION_CSV_FILE_PATH = settings.PBF_FILE_SIZE_ESTIMATION_CSV_FILE_PATH
