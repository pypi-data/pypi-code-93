import pytest
import socket

from seeq import spy
from seeq.sdk import Configuration, UserOutputV1

from seeq.spy.tests import test_common

from seeq.spy import _config, _login


@pytest.mark.system
def test_bad_login():
    test_common.login()

    Configuration().retry_timeout_in_seconds = 0

    with pytest.raises(RuntimeError):
        spy.login('mark.derbecker@seeq.com', 'DataLab!', url='https://bogus')

    assert spy.client is None
    assert spy.user is None

    # Remove overrides that resulted from spy.login() with bogus URL
    _config.unset_seeq_url()

    with pytest.raises(ValueError):
        spy.login('mark.derbecker@seeq.com', 'DataLab!', auth_token='Got any cheese?')

    assert spy.client is None
    assert spy.user is None


@pytest.mark.system
def test_good_login():
    test_common.login()

    assert spy.client is not None
    assert isinstance(spy.user, UserOutputV1)
    assert spy.user.username == 'agent_api_key'
    assert _config.Setting.SEEQ_URL.get() is None      # Should not be set, since we're using the default

    # force=False will mean that we don't try to login since we're already logged in
    spy.login(username='blah', password='wrong', force=False)

    assert spy.client is not None
    assert isinstance(spy.user, UserOutputV1)
    assert spy.user.username == 'agent_api_key'
    assert _config.Setting.SEEQ_URL.get() is None

    auth_token = spy.client.auth_token
    _login.client = None
    spy.client = None

    # Data Lab uses this pattern, and so we have to support it. We use gethostname() here just to make sure that the
    # default of http://localhost:34216 is not being used.
    url = f'http://{socket.gethostname()}:34216'
    spy._config.set_seeq_url(url)

    spy.login(auth_token=auth_token)
    assert spy.client is not None

    # If we login again we want to make sure the session was not invalidated and auth_token is still valid
    spy.login(auth_token=auth_token)

    assert spy.client is not None
    assert isinstance(spy.user, UserOutputV1)
    assert spy.user.username == 'agent_api_key'
    assert _config.Setting.SEEQ_URL.get() == url

    # Make sure we can do a simple search
    df = spy.search({'Name': 'Area A_Temperature'})
    assert len(df) > 0


@pytest.mark.system
def test_login_with_private_url():
    test_common.login(private_url=f'http://{socket.gethostname()}:34216')
    assert spy.client is not None
    assert isinstance(spy.user, UserOutputV1)
    assert spy.user.username == 'agent_api_key'


@pytest.mark.system
def test_good_login_user_switch():
    # login and get the token
    test_common.login()
    auth_token = spy.client.auth_token
    assert spy.user.username == 'agent_api_key'

    # create the state where kernel has no spy.user attached yet
    spy.client = None
    spy.user = None

    # do the initial auth_token login
    spy.login(auth_token=auth_token)
    assert spy.user.username == 'agent_api_key'

    # create another user
    test_common.login(admin=True)
    user_janna = test_common.add_normal_user('Janna', 'Contact', 'janna@seeq.com', 'jannacontact')

    # change the user inside the notebook
    spy.login(username='janna@seeq.com', password='jannacontact')
    assert spy.user.username == user_janna.username

    # login again as when re-opening the notebook
    spy.login(auth_token=auth_token)
    assert spy.user.username == 'agent_api_key'


@pytest.mark.system
def test_credentials_file_with_username():
    with pytest.raises(ValueError):
        spy.login('mark.derbecker@seeq.com', 'DataLab!', credentials_file='credentials.key')


@pytest.mark.unit
def test_validate_seeq_server_version():
    module_major, module_minor, module_patch, module_functional = _login.get_module_version_tuple()

    spy.options.allow_version_mismatch = True

    status = spy.Status()
    spy.server_version = 'R22.0.36.01-v202007160902-SNAPSHOT'
    seeq_server_major, seeq_server_minor, seeq_server_patch = _login.validate_seeq_server_version(status)
    assert len(status.warnings) == 1
    assert 'The major/minor version' in status.warnings.pop()
    assert (seeq_server_major, seeq_server_minor, seeq_server_patch) == (0, 36, 1)

    status = spy.Status()
    spy.server_version = 'R5000000.21.06-v203008100902-BETA'
    seeq_server_major, seeq_server_minor, seeq_server_patch = _login.validate_seeq_server_version(status)
    assert len(status.warnings) == 1
    assert 'The major version' in status.warnings.pop()
    assert (seeq_server_major, seeq_server_minor, seeq_server_patch) == (5000000, 21, 6)

    status = spy.Status()
    spy.server_version = f'R{module_major}.{module_minor}.{module_patch}'
    seeq_server_major, seeq_server_minor, seeq_server_patch = _login.validate_seeq_server_version(status)
    assert len(status.warnings) == 0
    assert (seeq_server_major, seeq_server_minor, seeq_server_patch) == (module_major, module_minor, module_patch)

    spy.options.allow_version_mismatch = False

    status = spy.Status()
    spy.server_version = 'R22.0.36.01-v202007160902-SNAPSHOT'
    with pytest.raises(RuntimeError, match=r'The major/minor version'):
        _login.validate_seeq_server_version(status)
