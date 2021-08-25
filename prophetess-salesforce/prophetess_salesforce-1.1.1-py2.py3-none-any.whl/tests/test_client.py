
import pytest
import asynctest
import aiohttp

from unittest.mock import patch

from prophetess_salesforce.client import SFClient
from prophetess_salesforce.exceptions import SalesforceAPIException


def test_SFClient():
    sfc = SFClient(client_id='test', user='tester', key='private-key', instance='na1')

    assert 'test' == sfc.client_id
    assert 'tester' == sfc.user
    assert 'private-key' == sfc.key
    assert 'na1' == sfc.instance


def test_SFClient_headers():
    sfc = SFClient(client_id='test', user='tester', key='key', instance='na1')
    sfc.token = 'secret-auth.token-probably-jwt'

    assert {'Authorization': 'Bearer secret-auth.token-probably-jwt'} == sfc.headers


def test_SFClient_build_url():
    sfc = SFClient(client_id='test', user='tester', key='key', instance='na1')

    versioned_url = sfc.build_url('v40.12')
    assert 'https://na1.salesforce.com/services/data/v40.12' == versioned_url


@pytest.mark.asyncio
async def test_SFClient_authenticate():
    with patch.object(SFClient, 'get_access_token', new_callable=asynctest.CoroutineMock) as mat:
        sf = SFClient(client_id='test', user='tester', key='key', instance='na1')
        await sf.authenticate()

        mat.assert_called_once()
        assert mat.return_value == sf.token


@pytest.mark.asyncio
@patch('prophetess_salesforce.client.jwt')
async def test_SFClient_get_access_token(mjwt):
    with patch.object(SFClient, 'request', new_callable=asynctest.CoroutineMock) as mreq:
        mreq.return_value = {'access_token': 'i am safe'}
        mjwt.encode.return_value = 'assertions'

        sfc = SFClient(client_id='test', user='tester', key='key', instance='na1')

        token = await sfc.get_access_token()

        assert 'i am safe' == token
        mreq.assert_called_with(
            'POST',
            'https://login.salesforce.com/services/oauth2/token',
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            data={
                'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
                'assertion': 'assertions',
            }
        )


@pytest.mark.asyncio
@patch('prophetess_salesforce.client.jwt')
async def test_SFClient_get_access_token_errors(mjwt):
    with patch.object(SFClient, 'request', new_callable=asynctest.CoroutineMock) as mreq:
        mreq.side_effect = [aiohttp.ClientError(), {'this is a bad': 'payload'}]

        sfc = SFClient(client_id='test', user='tester', key='key', instance='na1')

        with pytest.raises(SalesforceAPIException):
            # Test for aiohttp exceptions
            await sfc.get_access_token()

        with pytest.raises(SalesforceAPIException):
            # Test for bad access token / malformed response
            await sfc.get_access_token()


@pytest.mark.asyncio
@asynctest.patch('prophetess_salesforce.client.aiohttp')
async def test_SFClient_request(maiohttp):
    maiohttp.request.return_value.__aenter__.return_value.json = asynctest.CoroutineMock()
    maiohttp.request.return_value.__aenter__.return_value.json.return_value = {'test': 'success'}

    sfc = SFClient(client_id='test', user='tester', key='key', instance='na1')
    ret = await sfc.request('GET', 'url', params={'foo': 'bar'}, data='best')

    assert {'test': 'success'} == ret
    assert maiohttp.request.called_with(
        'GET',
        'url',
        headers={'Authorization': 'Bearer None'},
        data='best',
        params={'foo', 'bar'}
    )


@pytest.mark.asyncio
async def test_SFCLient_run_query():
    with patch.object(SFClient, 'request', new_callable=asynctest.CoroutineMock) as mreq:
        mreq.return_value = {'records': ['hello', 'one', 'three']}

        sfc = SFClient(client_id='test', user='tester', key='key', instance='na1')

        data = await sfc.run_query('SELECT Id FROM Accounts')
        assert ['hello', 'one', 'three'] == data

        mreq.assert_called_with(
            'GET',
            'https://na1.salesforce.com/services/data/v41.0/query',
            params={
                'q': 'SELECT Id FROM Accounts',
            }
        )


@pytest.mark.asyncio
async def test_SFCLient_run_query_errors():
    with patch.object(SFClient, 'request', new_callable=asynctest.CoroutineMock) as mreq:
        mreq.side_effect = [aiohttp.ClientError(), {'this is a bad': 'payload'}]

        sfc = SFClient(client_id='test', user='tester', key='key', instance='na1')

        with pytest.raises(SalesforceAPIException):
            await sfc.run_query('SELECT Id FROM Accounts')

        with pytest.raises(SalesforceAPIException):
            await sfc.run_query('SELECT Id FROM Accounts')
