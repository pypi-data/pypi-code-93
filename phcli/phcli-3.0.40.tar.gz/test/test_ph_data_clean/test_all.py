import os
import pytest
from phcli.ph_data_clean.__main__ import clean
from phcli.ph_data_clean.util.yaml_utils import load_by_dir
from phcli.ph_data_clean.model.clean_result import Tag

PROJECT_NAME = 'phdagcommand'


@pytest.mark.skip("util")
def chdir():
    if not os.getcwd().endswith(PROJECT_NAME):
        os.chdir('..')
        chdir()


chdir()


def test_all():
    test_files = 'file/ph_data_clean/s3_test_data/'
    test_datas = load_by_dir(test_files)
    for test_data in test_datas:
        result = clean(test_data)
        for res in result:
            if res.tag == Tag.SUCCESS:
                print()
                print('success  ')
            elif res.tag == Tag.WARNING:
                print()
                print('warning  ', res.data["UPDATE_LABEL"], "    ", res.data["PHA_ID"], "    ", res.err_msg)
            else:
                print()
                print(str(res))


test_all()
