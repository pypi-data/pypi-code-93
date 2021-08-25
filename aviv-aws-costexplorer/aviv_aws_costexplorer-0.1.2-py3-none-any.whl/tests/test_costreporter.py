import pytest
import botocore.client
import aviv_aws_costexplorer.costreporter as cr



def test_basic():
    obj = cr.CostReporter()
    assert isinstance(obj, cr.CostReporter)

def test_flatten_amounts():
    amount = {"Total": {"UnblendedCost": {"Amount": 42.42, "Unit": "USD"}, "BlendedCost": {"Amount": 42.42, "Unit": "USD"}}}
    flat_amount = cr.CostReporter.flatten_amounts(amounts=amount['Total'])
    assert 'UnblendedCost' in flat_amount
    assert 'BlendedCost' in flat_amount

def test_metadata():
    rec = {"TimePeriod": {"Start": "yyyy", "End": "yyyy"}}
    obj = cr.CostReporter()

    cr.AWS_CE_REQUESTID = '1'
    obj._stamp_record(rec, {"RequestId": "xxxxx-yyyyy"})
    assert 'Start' in rec
    assert 'End' in rec
    assert 'RequestId' in rec

def test_connection():
    # can we assume role?
    obj = cr.CostReporter()
    assert isinstance(obj.sts, botocore.client.BaseClient)
    assert str(obj.sts.__class__) == "<class 'botocore.client.STS'>"

def test_stamp_record_period():
    obj = cr.CostReporter()

    obj.granularity='monthly'
    record = {"TimePeriod": {"Start": "2021-04-21"}}
    obj._stamp_record(record, {})
    assert record['Period'] == "202104"

    record = {"TimePeriod": {"Start": "2021-04-20T13:45:30"}}
    obj._stamp_record(record, {})
    assert record['Period'] == "202104"

    obj.granularity = 'daily'
    record = {"TimePeriod": {"Start": "2021-04-20T13:45:30"}}
    obj._stamp_record(record, {})
    assert record['Period'] == "20210420"
