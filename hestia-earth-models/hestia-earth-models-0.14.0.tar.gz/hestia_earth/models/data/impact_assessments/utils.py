import os
import sys


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(CURRENT_DIR + "/")


def get_dir(): return os.environ.get('DOWNLOAD_DIR', CURRENT_DIR)
