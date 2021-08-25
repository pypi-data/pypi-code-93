
import pytest
import asynctest

from unittest.mock import patch

from prophetess_salesforce.extractor import SalesforceExtractor
from prophetess_salesforce.exceptions import SalesforceAPIException


@patch('prophetess_salesforce.extractor.SFClient')
def test_SalesforceExtractor(msfc):
    config = {
        'client_id': 'test',
        'user': 'tester',
        'instance': 'na999',
        'key': 'private-key',
        'query': 'SELECT Id, Name from Accounts',
    }

    sfe = SalesforceExtractor(id='testextract', config=config)
    assert msfc.return_value == sfe.sf

    msfc.assert_called_with(
        client_id='test',
        user='tester',
        key='private-key',
        instance='na999'
    )


@pytest.mark.asyncio
@patch('prophetess_salesforce.extractor.SFClient')
async def test_SalesforceExtractor_run(msfc):
    config = {
        'client_id': 'test',
        'user': 'tester',
        'instance': 'na999',
        'key': 'private-key',
        'query': 'SELECT Id, Name from Accounts',
    }

    msfc.return_value.authenticate = asynctest.CoroutineMock()
    msfc.return_value.run_query = asynctest.CoroutineMock()
    msfc.return_value.run_query.return_value = ['one', 'two']

    sfe = SalesforceExtractor(id='testextract', config=config)
    assert ['one', 'two'] == [d async for d in sfe.run()]


@pytest.mark.asyncio
@patch('prophetess_salesforce.extractor.SFClient')
async def test_SalesforceExtractor_run_error(msfc):
    config = {
        'client_id': 'test',
        'user': 'tester',
        'instance': 'na999',
        'key': 'private-key',
        'query': 'SELECT Id, Name from Accounts',
    }

    msfc.return_value.authenticate = asynctest.CoroutineMock()
    msfc.return_value.run_query = asynctest.CoroutineMock()
    msfc.return_value.run_query.side_effect = [SalesforceAPIException]

    with pytest.raises(SalesforceAPIException):
        sfe = SalesforceExtractor(id='testextract', config=config)
        assert ['one', 'two'] == [d async for d in sfe.run()]
