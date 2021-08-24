import os
import tempfile
from pathlib import Path

from jinja2 import Template

MINI_ESGF_CACHE_DIR = Path.home() / ".mini-esgf-data"
PICKLE_CFG = os.path.join(tempfile.gettempdir(), "config.ini")


def write_cfg():
    cfg_templ = """
    [paths]
    dir_grouping_level = 4
    pickle_dirs = {{ tmp_dir }}/fakedir/ {{ tmp_dir }}/otherdir
    writeable_pickle_dir = {{ tmp_dir }}/otherdir
    archive_dir = {{ base_dir }}/master/test_data/badc/cmip6/data
    remove_archive_dir_in_path = True
    """
    cfg = Template(cfg_templ).render(
        base_dir=MINI_ESGF_CACHE_DIR, tmp_dir=tempfile.gettempdir()
    )
    with open(PICKLE_CFG, "w") as fp:
        fp.write(cfg)
    # point to cfg in environment
    os.environ["PICKLE_CONFIG"] = PICKLE_CFG
