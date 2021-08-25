import pytest
import datetime
import dateutil.relativedelta
from aviv_aws_costexplorer import costexplorer

m3ago = (datetime.datetime.now().date() - dateutil.relativedelta.relativedelta(months=3))
m6ago = (datetime.datetime.now().date() - dateutil.relativedelta.relativedelta(months=6))

@pytest.fixture
def aace():
    return costexplorer.CostExplorer()


def test_date(aace):
    assert isinstance(aace, costexplorer.CostExplorer)
    assert datetime.datetime.now().strftime('%Y-%m-01') == aace.period['End']

    obj2 = costexplorer.CostExplorer(date=datetime.datetime.now(), period=dict(months=3))
    assert datetime.datetime.now().strftime('%Y-%m-01') == obj2.period['End']
    assert m3ago.strftime('%Y-%m-01') == obj2.period['Start']

    obj3 = costexplorer.CostExplorer(date=m3ago, period=dict(months=3))
    assert m3ago.strftime('%Y-%m-01') == obj3.period['End']
    assert m6ago.strftime('%Y-%m-01') == obj3.period['Start']


def test_daily():
    obj = costexplorer.CostExplorer(granularity='daily', date=datetime.datetime.now(), period=dict(months=3))
    assert str(datetime.datetime.now().date()) == obj.period['End']
    assert str(m3ago) == obj.period['Start']

    obj2 = costexplorer.CostExplorer(granularity='daily', date=m3ago, period=dict(months=3))
    assert str(m3ago) == obj2.period['End']
    assert str(m6ago) == obj2.period['Start']

def test_hourly():
    obj = costexplorer.CostExplorer(date=datetime.datetime.now(), granularity='hourly')
    assert datetime.datetime.now().strftime('%Y-%m-%dT00:00:00Z') == obj.period['End']
