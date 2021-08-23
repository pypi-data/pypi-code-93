from . import BasicDataIgnition
from hg_delivery.models.hgd_model import Project
import transaction
from mock import MagicMock, Mock
from mock_alchemy.mocking import AlchemyMagicMock
from pyramid import testing
from unittest.mock import patch
from sqlalchemy.exc import OperationalError


# testing  delete_project, node_description


class TestProject(BasicDataIgnition):
    def setUp(self):

        self.config = testing.setUp(
            settings={'sqlalchemy.url': 'sqlite:///:memory:'})
        self.config.include('..models')
        settings = self.config.get_settings()
        settings['sqlalchemy.echo'] = False

        import logging

        from ..models import (
            get_engine,
            get_session_factory,
            get_tm_session,
        )

        from ..models.meta import (
            Base,
        )

        self.engine = get_engine(settings)
        session_factory = get_session_factory(self.engine)
        Base.metadata.create_all(bind=self.engine)
        self.session = get_tm_session(session_factory, transaction.manager)

        logging.disable(logging.CRITICAL)

        # add a user
        self.users_list = self._add_some_user()

    def test_add_project(self):
        from ..views import add_project
        from ..nodes import PoolSsh
        from ..models.hgd_model import Project

        request = testing.DummyRequest()
        request.dbsession = self.session
        result = add_project(request)
        self.assertFalse(result['result'])
        self.assertEqual(result['explanation'], 'Missing project name')
        request.params['name'] = 'p1'
        result = add_project(request)
        self.assertFalse(result['result'])
        self.assertEqual(result['explanation'], 'Missing project user')
        request.params['user'] = 'dev'
        result = add_project(request)
        self.assertFalse(result['result'])
        self.assertEqual(result['explanation'], 'Missing project host')
        request.params['host'] = '127.0.0.1'
        result = add_project(request)
        self.assertFalse(result['result'])
        self.assertEqual(result['explanation'], 'Missing project path')
        request.params['path'] = './'
        result = add_project(request)
        self.assertFalse(result['result'])
        str_output = 'Your project should contains password or local pkey'
        self.assertEqual(result['explanation'], str_output)

        # first call get success
        cls_mmock = MagicMock()
        # mock initial hash
        cls_mmock.get_initial_hash.return_value = '3423424242424242442342'
        with patch.object(PoolSsh, 'get_node', return_value=cls_mmock):
            request.params['password'] = 'pass'
            result = add_project(request)
            self.assertTrue(result['result'])
            str_output = 'This project : dev@127.0.0.1/./ has been added ...'
            self.assertEqual(result['explanation'], str_output)

        # check project item has been created
        nb_projects = self.session.query(Project).count()
        self.assertEqual(nb_projects, 1)

        # second call generate error
        cls_mmock = MagicMock()
        # mock initial hash
        cls_mmock.get_initial_hash.return_value = '3423424242424242442342'
        with patch.object(PoolSsh, 'get_node', return_value=cls_mmock):
            request.params['password'] = 'pass'
            result = add_project(request)
            self.assertFalse(result['result'])
            str_output = 'This project and this path are'
            str_output += ' already defined (127.0.0.1 ./) ...'
            self.assertEqual(result['explanation'], str_output)

        # database is not available
        request = testing.DummyRequest()
        request.params['name'] = 'p1'
        request.params['user'] = 'dev'
        request.params['host'] = '127.0.0.1'
        request.params['path'] = './'

        cls_mmock = MagicMock()
        exception_mock = OperationalError(None, None, 'database timeout')
        request.dbsession = self.session
        request.dbsession.add = Mock()
        request.dbsession.add.side_effect = exception_mock
        request.dbsession.add.raiseError.side_effect = exception_mock
        with patch.object(PoolSsh, 'get_node', return_value=cls_mmock):
            request.params['local_pkey'] = '1'
            request.params['password'] = 'pass'
            result = add_project(request)
            self.assertFalse(result['result'])
            # str formated error
            str_output = '(builtins.str) database timeout\n'
            str_output += '(Background on this error at:'
            str_output += ' http://sqlalche.me/e/14/e3q8)'
            self.assertEqual(result['explanation'], str_output)

        # to be continued
        # bad ignition
        # pkey not available
        # host not joinable
        # wrong password

    def test_delete_project(self):
        from ..views import delete_project
        (p_a, p_b) = self._add_some_projects()

        # missing parameter
        request = testing.DummyRequest()
        request.dbsession = self.session
        result = delete_project(request)
        self.assertFalse(result['result'])
        self.assertEqual(result['error'], 'bad parameter')

        # delete first project
        request = testing.DummyRequest()
        request.dbsession = self.session
        request.matchdict['id'] = p_a.id
        result = delete_project(request)
        self.assertTrue(result['result'])
        self.assertIsNone(result['error'])
        cpt = self.session.query(Project).count()
        self.assertEqual(cpt, 1)

        # delete second project
        request.matchdict['id'] = p_b.id
        result = delete_project(request)
        self.assertTrue(result['result'])
        self.assertIsNone(result['error'])
        cpt = self.session.query(Project).count()
        self.assertEqual(cpt, 0)

        # project doesn't exist any more
        request.matchdict['id'] = p_b.id
        result = delete_project(request)
        self.assertFalse(result['result'])
        self.assertEqual(result['error'], 'unknown project')

    def test_delete_unknown_project(self):
        """ """
        from ..views import delete_project

        # raise alchemy error
        request = testing.DummyRequest()
        request.matchdict['id'] = 42
        request.dbsession = AlchemyMagicMock()
        exception_mock = OperationalError(None, None, 'database timeout')
        request.dbsession.query = Mock()
        request.dbsession.query.side_effect = exception_mock
        request.dbsession.query.raiseError.side_effect = exception_mock
        request.matchdict['id'] = 1
        result = delete_project(request)
        self.assertFalse(result['result'])
        self.assertEqual(result['error'], 'database timeout')

        # delete with mock to raise standard error
        request = testing.DummyRequest()
        request.matchdict['id'] = 42
        request.dbsession = AlchemyMagicMock()
        exception_mock = Exception('standard error')
        request.dbsession.query = Mock()
        request.dbsession.query.side_effect = exception_mock
        request.dbsession.query.raiseError.side_effect = exception_mock
        result = delete_project(request)
        self.assertFalse(result['result'])
        self.assertEqual(result['error'], 'standard error')

        # delete random unknown project
        request = testing.DummyRequest()
        request.dbsession = self.session
        request.matchdict['id'] = 42
        result = delete_project(request)
        self.assertFalse(result['result'])
        self.assertEqual(result['error'], 'unknown project')

    def test_delete_project_missing_db(self):
        """
            raise an exception
        """
        from ..views import delete_project
        request = testing.DummyRequest()
        request.dbsession = self.session

        # delete first project
        request.matchdict['id'] = 42
        result = delete_project(request)
        self.assertFalse(result['result'])
        self.assertEqual(result['error'], 'unknown project')

    def project_nominal_behavior(self):
        pass

    def project_missing_arguments(self):
        pass

# -----------------------------------------------------------------------------


class TestNode(BasicDataIgnition):
    """
    """

    def setUp(self):

        self.config = testing.setUp(
            settings={'sqlalchemy.url': 'sqlite:///:memory:'})
        self.config.include('..models')
        settings = self.config.get_settings()

        from ..models import (
            get_engine,
            get_session_factory,
            get_tm_session,
        )

        from ..models.meta import (
            Base,
        )

        self.engine = get_engine(settings)
        session_factory = get_session_factory(self.engine)
        Base.metadata.create_all(bind=self.engine)
        self.session = get_tm_session(session_factory, transaction.manager)

        # add a user
        self.users_list = self._add_some_user()

    def test_node_description(self):
        """
        """
        from ..views import node_description
        from ..nodes import PoolSsh
        import json

        p1, p2 = self._add_some_projects()
        request = testing.DummyRequest()
        request.dbsession = AlchemyMagicMock()
        exception_mock = OperationalError(None, None, 'database timeout')
        request.dbsession.query = Mock()
        request.dbsession.query.side_effect = exception_mock
        request.dbsession.query.raiseError.side_effect = exception_mock

        request.matchdict['id'] = p1.id
        result = node_description(request)
        self.assertFalse(result['result'])
        self.assertEqual(result['repository_error'], 'database timeout')

        request = testing.DummyRequest()
        request.dbsession = self.session
        request.matchdict['id'] = p1.id
        cls_mmock = MagicMock()

        str_json = '''{"node": "42899a2fdea14029f5e13519f34ca5f6c47d41d4",
                       "p1node": "c9abeecad1597c5384de2d9a07f7a573017cb01a",
                       "p2node": null,
                       "branch": "default",
                       "author": "stephane.bard@gmail.com",
                       "rev": "3",
                       "parents": "",
                       "desc": "third_commit_d2",
                       "tags": "\\n",
                       "date": "2021-06-05 16:13 +0200"}'''
        returned_data = json.loads(str_json)
        cls_mmock.get_current_revision_description.return_value = returned_data

        with patch.object(PoolSsh, 'get_node', return_value=cls_mmock):
            result = node_description(request)
            self.assertTrue(result['result'])
            self.assertEqual(result['node_description']['node'],
                             '42899a2fdea14029f5e13519f34ca5f6c47d41d4')
