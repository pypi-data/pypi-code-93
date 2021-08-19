import pytest

from re_common.baselibrary.utils.mfaker import MFaker


# pytest mfaker_test.py -s
# -s 打印print的结果
def test_faker_dict():
    fake = MFaker()
    dicts = fake.create_data(MFaker.m_pydict, **fake.py_para())
    print(dicts)
    print(len(dicts))
    assert type(dicts) == dict

# pytest mfaker_test.py::test_faker_list -s
# 测试单独的一个test
def test_faker_list():
    fake = MFaker()
    lists = fake.create_data(MFaker.m_pylist, **fake.py_para())
    print(lists)
    print(len(lists))
    assert type(lists) == list







