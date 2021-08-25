import pytest
import pandas as pd
import goldenowl.portfolio.holding as hd
import goldenowl.portfolio.portfolio as pf
import goldenowl.asset.asset as at

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
    tup = list(zip(price_dict.keys(), price_dict.values()));
    data = pd.DataFrame(tup, columns=['Date', 'Close']);
    data['Open'] = data['High'] = data['Low'] = 0;
    return data;

def test_addAmount():
    asset1 = at.Asset('Asset1', get_prdata());
    asset2 = at.Asset('Asset2', get_prdata());
    asset_ratio_list = [(asset1, 0.4), (asset2, 0.6)]
    prtf = pf.Portfolio('TestP', asset_ratio_list);

    hldng1 =hd.Holding('Test1', asset1);
    hldng2 =hd.Holding('Test2', asset2);
    prtf.addAmount(200, '1992-11-23');
    val = prtf.getValue('2012-01-23');

    hldng1.buyAmount(200*0.4, '1992-11-23');
    hldng2.buyAmount(200*0.6, '1992-11-23');
    valh1 = hldng1.getValue('2012-01-23');
    valh2 = hldng2.getValue('2012-01-23');
    assert (val) == (valh1+ valh2), "addAmount failed"

def test_removeAmount():
    asset1 = at.Asset('Asset1', get_prdata());
    asset2 = at.Asset('Asset2', get_prdata());
    asset_ratio_list = [(asset1, 0.4), (asset2, 0.6)]
    prtf = pf.Portfolio('TestP', asset_ratio_list);

    hldng1 =hd.Holding('Test1', asset1);
    hldng2 =hd.Holding('Test2', asset2);
    prtf.addAmount(200, '1992-11-23');
    prtf.removeAmount(100, '2000-10-03');
    val = prtf.getValue('2012-01-23');

    hldng1.buyAmount(200*0.4, '1992-11-23');
    hldng2.buyAmount(200*0.6, '1992-11-23');
    hldng1.sellAmount(100*0.4, '2000-10-03');
    hldng2.sellAmount(100*0.6, '2000-10-03');
    valh1 = hldng1.getValue('2012-01-23');
    valh2 = hldng2.getValue('2012-01-23');
    assert (val) == (valh1+ valh2), "removeAmount failed"

def test_rebalance():
    asset1 = at.Asset('Asset1', get_prdata());
    pr_data = get_prdata();
    pr_data.loc[pr_data.Date == pd.to_datetime("2000-10-03"), ['Close']] = 200;
    pr_data.loc[pr_data.Date == pd.to_datetime("2012-01-23"), ['Close']] = 3000;
    asset2 = at.Asset('Asset2', pr_data);
    asset_ratio_list = [(asset1, 0.4), (asset2, 0.6)]

    prtf = pf.Portfolio('TestP', asset_ratio_list);
    prtf.addAmount(200, '1992-11-23');
    prtf.removeAmount(100, '2000-10-03');

    final_val = prtf.getValue('2012-01-23');
    val_bef_rebalance = prtf.getValue('2000-10-03');
    prtf.rebalance('2000-10-03');
    hldng1 =hd.Holding('Test1', asset1);
    hldng2 =hd.Holding('Test2', asset2);
    hldng1.buyAmount(val_bef_rebalance*0.4, '2000-10-03');
    hldng2.buyAmount(val_bef_rebalance*0.6, '2000-10-03');

    hldval1= hldng1.getValue('2012-01-23');
    hldval2= hldng2.getValue('2012-01-23');
    final_val_rb = prtf.getValue('2012-01-23');

    assert (final_val_rb) == pytest.approx(hldval1 + hldval2,0.1), "post rebalance tally failed"
    assert (final_val_rb) != pytest.approx(final_val, 0.1), "post and pre rebalance same"


def test_XIRR():
    asset1 = at.Asset('Asset1', get_prdata());
    pr_data = get_prdata();
    pr_data.loc[pr_data.Date == pd.to_datetime("2000-10-03"), ['Close']] = 200;
    pr_data.loc[pr_data.Date == pd.to_datetime("2012-01-23"), ['Close']] = 3000;
    asset2 = at.Asset('Asset2', pr_data);
    asset_ratio_list = [(asset1, 0.4), (asset2, 0.6)]

    prtf = pf.Portfolio('TestP', asset_ratio_list);
    prtf.addAmount(200, '1992-11-23');
    prtf.removeAmount(100, '2000-10-03');
    val = prtf.getXIRR('2012-01-23');

    assert (val) == pytest.approx(0.092,0.1), "XIRR failed"


def test_SIP():
    asset1 = at.Asset('Asset1', get_prdata());
    pr_data = get_prdata();
    pr_data.loc[pr_data.Date == pd.to_datetime("2000-10-03"), ['Close']] = 200;
    pr_data.loc[pr_data.Date == pd.to_datetime("2012-01-23"), ['Close']] = 3000;
    asset2 = at.Asset('Asset2', pr_data);
    asset_ratio_list = [(asset1, 0.4), (asset2, 0.6)]
    sip_r = pf.getSIPReturn(asset_ratio_list, 30, 90, '1990-11-23', '2020-11-11') 
    assert sip_r == pytest.approx(0.157,0.1), "SIP calculation failed"
