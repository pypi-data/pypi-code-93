import pytest
import pandas as pd
import goldenowl.portfolio.holding as hd

def get_prdata():
    price_dict_raw ={
                '1992-11-23': 234.2,
                '1999-01-23': 34.2,
                '2000-10-03': 134.2,
                '2001-11-01': 333.9,
                '2002-11-23': 234.2,
                '2005-05-2': 100,
                '2012-01-23': 4000.0,
                };
    price_dict = {pd.to_datetime(key):val for key, val in price_dict_raw.items()} 
    return price_dict;

def test_buyUnits():
    price_dict = get_prdata();
    hldng =hd.Holding('Test', price_dict);
    hldng.buyUnits(10, '1992-11-23');
    val = hldng.getHoldingValue('2012-01-23');
    assert (val) == 40000, "buyUnits failed"

def test_sellUnits():
    price_dict = get_prdata();
    hldng =hd.Holding('Test', price_dict);
    hldng.buyUnits(10, '1992-11-23');
    hldng.sellUnits(5, '2001-11-01');
    val = hldng.getHoldingValue('1999-01-23');
    assert val == 342, "buyUnits failed"
    val = hldng.getHoldingValue('2005-05-2');
    assert val == 500, "buyUnits failed"

def test_AmountTx():
    price_dict = get_prdata();
    hldng =hd.Holding('Test', price_dict);
    hldng.buyUnits(10, '1992-11-23');
    hldng.sellAmount(2000, '2001-11-01');
    val = hldng.getHoldingValue('1999-01-23');
    assert val == 342, "buyUnits failed"
    val = hldng.getHoldingValue('2005-05-2');
    assert val == pytest.approx(401.018, 0.1), "buyUnits failed"

def test_AmountTx():
    price_dict = get_prdata();
    hldng =hd.Holding('Test', price_dict);
    hldng.buyUnits(10, '1992-11-23');
    hldng.buyAmount(100, '1992-11-23');
    hldng.sellAmount(2000, '2001-11-01');
    val = hldng.getHoldingValue('1999-01-23');
    assert val == pytest.approx(356.6, 0.1), "HoldingValue failed"
    val = hldng.getHoldingValue('2005-05-2');
    assert val == pytest.approx(443.7, 0.1), "HoldingValue failed"
    xir_val = hldng.getXIRR('2012-01-23');
    assert xir_val == pytest.approx(0.12, 0.1), "XIRR failed"


def test_SIP():
    price_dict = get_prdata();
    sip_r = hd.getSIPReturn(price_dict, 30,'1990-11-23', '2020-11-11') 
    assert sip_r == pytest.approx(0.29,0.1), "SIP calculation failed"
