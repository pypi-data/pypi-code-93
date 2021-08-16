import os
import pytest
from phcli.ph_data_clean.__main__ import clean
from phcli.ph_data_clean.util.yaml_utils import load_by_file
from phcli.ph_data_clean.model.clean_result import Tag

PROJECT_NAME = 'phdagcommand'


@pytest.mark.skip("util")
def chdir():
    if not os.getcwd().endswith(PROJECT_NAME):
        os.chdir('..')
        chdir()


chdir()


def test_all():
    test_file = r'file/ph_data_clean/s3_test_data/product-product-test.yaml'
    test_datas = load_by_file(test_file)
    for test_data in test_datas:
        result = clean(test_data)
        for res in result:
            if res.tag == Tag.SUCCESS:
                print()
                print('success  ', res.data)
            elif res.tag == Tag.WARNING:
                print()
                print('warning  ', res.err_msg, res.data)
            else:
                print()
                print(str(res))


test_all()
