import pytest
import pandas as pd
import goldenowl.asset.asset as at

def get_prdata():
    date_range =[elem for elem in pd.date_range(start="1990-01-01",end="2000-01-01", freq='1D')];
    price_dict ={ date_range[i] : i+1 for i in range(0,len(date_range))}
    tup = list(zip(price_dict.keys(), price_dict.values()));
    data = pd.DataFrame(tup, columns=['Date', 'Close']);
    data['Open'] = data['High'] = data['Low'] = 0;
    return data;

def test_Value():
    pr_d = get_prdata();
    inst = at.Asset('Test', pr_d);
    val = inst.getValue("1993-01-01");
    name = inst.getName();
    assert name == "Test", "Asset name incorrect"
    assert (val) == 1097, "Asset value retrieval failed"
    val1 = inst.getValue("2000-01-01");
    val2 = inst.getValue("2021-01-01");
    assert val1 == val2, "Nearest Asset value retrieval failed"

def test_Returns():
    pr_d = get_prdata();
    inst = at.Asset('Test', pr_d);

    val = inst.getReturnsTimeFrame('1W');
    assert type(val) == type(pd.Series()), "Asset 1W Returns type mismatch"
    assert val.mean() ==  pytest.approx(0.024, 0.1), "Asset 1W Returns data incorrect"

    val = inst.getReturnsTimeFrame('1D');
    assert type(val) == type(pd.Series()), "Asset 1D Returns type mismatch"
    assert val.mean() ==  pytest.approx(0.0024, 0.1), "Asset 1D Returns data incorrect"

def test_Range():
    pr_d = get_prdata();
    inst = at.Asset('Test', pr_d);

    val = inst.getRangeTimeFrame('1W');
    assert type(val) == type(pd.Series()), "Asset 1W Returns type mismatch"
    assert val.mean() ==  pytest.approx(6.99, 0.1), "Asset 1W Returns data incorrect"

    val = inst.getRangeTimeFrame('1D');
    assert type(val) == type(pd.Series()), "Asset 1D Returns type mismatch"
    assert val.mean() ==  pytest.approx(1.0, 0.1), "Asset 1D Returns data incorrect"
