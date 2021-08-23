from . import BasicDataIgnition
import transaction
from mock import MagicMock, Mock
from mock_alchemy.mocking import AlchemyMagicMock
from pyramid import testing
from unittest.mock import patch
from sqlalchemy.exc import OperationalError


# ------------------------------------------------------------------------------


class TestPushPull(BasicDataIgnition):
    def setUp(self):

        self.config = testing.setUp(
            settings={'sqlalchemy.url': 'sqlite:///:memory:'})
        self.config.include('..models')
        settings = self.config.get_settings()

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
        self.projects_list = self._add_some_projects()

    def tearDown(self):
        transaction.abort()
        testing.tearDown()

    def test_shall_we_push(self):
        """
            mock HgNode behavior to pilot HgNode
            and test any view that push or pull
        """
        from ..nodes import PoolSsh
        from ..views import shall_we_push

        # bad parameters
        request = testing.DummyRequest()
        request.dbsession = self.session
        result = shall_we_push(request)
        self.assertFalse(result['result'])
        self.assertIsInstance(result['result'], bool)
        self.assertEqual(result['error'], 'bad parameter')

        request = testing.DummyRequest()
        request.matchdict['id'] = 1
        request.dbsession = self.session
        result = shall_we_push(request)
        self.assertFalse(result['result'])
        self.assertIsInstance(result['result'], bool)
        self.assertEqual(result['error'], 'bad parameter')

        request = testing.DummyRequest()
        request.matchdict['target'] = 2
        request.dbsession = self.session
        result = shall_we_push(request)
        self.assertFalse(result['result'])
        self.assertIsInstance(result['result'], bool)
        self.assertEqual(result['error'], 'bad parameter')

        cls_mmock = MagicMock()
        cls_mmock.pushable.return_value = True
        with patch.object(PoolSsh, 'get_node', return_value=cls_mmock):
            request = testing.DummyRequest()
            request.dbsession = self.session
            request.matchdict['id'] = 1
            request.matchdict['target'] = 2
            result = shall_we_push(request)
            self.assertTrue(result['result'])
            self.assertIsInstance(result['result'], bool)
            self.assertIsNone(result['error'])

        # second call, bc now node is in spool
        cls_mmock = MagicMock()
        cls_mmock.pushable.return_value = False
        with patch.object(PoolSsh, 'get_node', return_value=cls_mmock):
            request = testing.DummyRequest()
            request.dbsession = self.session
            request.matchdict['id'] = 1
            request.matchdict['target'] = 2
            result = shall_we_push(request)
            self.assertFalse(result['result'])
            self.assertIsNone(result['error'])

    def test_shall_we_push_unkown_project(self):
        """
            mock HgNode behavior to pilot HgNode
            and test any view that push or pull
        """
        from ..views import shall_we_push
        request = testing.DummyRequest()
        request.dbsession = self.session
        request.matchdict['id'] = 8
        request.matchdict['target'] = 9
        result = shall_we_push(request)
        self.assertFalse(result['result'],)
        self.assertEqual(result['error'], 'Unknown project')

        exception_mock = OperationalError(None, None, 'database timeout')
        request.dbsession.query = Mock()
        request.dbsession.query.side_effect = exception_mock
        request.dbsession.query.raiseError.side_effect = exception_mock
        result = shall_we_push(request)
        self.assertFalse(result['result'],)
        self.assertEqual(result['error'], 'database timeout')

        request.dbsession = AlchemyMagicMock()
        exception_mock = Exception('dummy error')
        request.dbsession.query = Mock()
        request.dbsession.query.side_effect = exception_mock
        request.dbsession.query.raiseError.side_effect = exception_mock
        result = shall_we_push(request)
        self.assertFalse(result['result'],)
        self.assertEqual(result['error'], 'dummy error')

    def test_shall_we_pull(self):
        """
            mock HgNode behavior to pilot HgNode
            and test any view that push or pull
        """
        from ..nodes import PoolSsh
        from ..views import shall_we_pull

        # bad parameters
        request = testing.DummyRequest()
        request.dbsession = self.session
        result = shall_we_pull(request)
        self.assertFalse(result['result'])
        self.assertIsInstance(result['result'], bool)
        self.assertEqual(result['error'], 'bad parameter')

        request = testing.DummyRequest()
        request.matchdict['id'] = 1
        request.dbsession = self.session
        result = shall_we_pull(request)
        self.assertFalse(result['result'])
        self.assertIsInstance(result['result'], bool)
        self.assertEqual(result['error'], 'bad parameter')

        request = testing.DummyRequest()
        request.matchdict['source'] = 2
        request.dbsession = self.session
        result = shall_we_pull(request)
        self.assertFalse(result['result'])
        self.assertIsInstance(result['result'], bool)
        self.assertEqual(result['error'], 'bad parameter')

        cls_mmock = MagicMock()
        cls_mmock.pullable.return_value = True
        with patch.object(PoolSsh, 'get_node', return_value=cls_mmock):
            request = testing.DummyRequest()
            request.dbsession = self.session
            request.matchdict['id'] = 1
            request.matchdict['source'] = 2
            result = shall_we_pull(request)
            self.assertTrue(result['result'])
            self.assertIsNone(result['error'])

        cls_mmock = MagicMock()
        cls_mmock.pullable.return_value = False
        with patch.object(PoolSsh, 'get_node', return_value=cls_mmock):
            request.matchdict['id'] = 1
            request.matchdict['source'] = 2
            result = shall_we_pull(request)
            self.assertFalse(result['result'])
            self.assertIsNone(result['error'])

    def test_shall_we_pull_unknown_project(self):
        """
            mock HgNode behavior to pilot HgNode
            and test any view that push or pull
        """
        from ..views import shall_we_pull
        request = testing.DummyRequest()
        request.dbsession = self.session
        request.matchdict['id'] = 8
        request.matchdict['source'] = 9
        result = shall_we_pull(request)
        self.assertFalse(result['result'],)
        self.assertEqual(result['error'], 'Unknown project')

        request.dbsession = AlchemyMagicMock()
        exception_mock = OperationalError(None, None, 'database timeout')
        request.dbsession.query = Mock()
        request.dbsession.query.side_effect = exception_mock
        request.dbsession.query.raiseError.side_effect = exception_mock
        result = shall_we_pull(request)
        self.assertFalse(result['result'],)
        self.assertEqual(result['error'], 'database timeout')

        request.dbsession = AlchemyMagicMock()
        exception_mock = Exception('dummy exception')
        request.dbsession.query = Mock()
        request.dbsession.query.side_effect = exception_mock
        request.dbsession.query.raiseError.side_effect = exception_mock
        result = shall_we_pull(request)
        self.assertFalse(result['result'],)
        self.assertEqual(result['error'], 'dummy exception')

    def test_direct_pull(self):
        from ..views import pull
        from ..nodes import PoolSsh
        p_1, p_2 = self.projects_list

        request = testing.DummyRequest()
        request.dbsession = self.session
        result = pull(request)
        self.assertFalse(result['result'])
        self.assertEqual(result['error'], 'bad parameter')

        request = testing.DummyRequest()
        request.dbsession = self.session
        request.matchdict['id'] = p_1.id
        result = pull(request)
        self.assertFalse(result['result'])
        self.assertEqual(result['error'], 'bad parameter')

        request = testing.DummyRequest()
        request.dbsession = self.session
        request.matchdict['id'] = p_1.id
        request.matchdict['source'] = p_2.id
        cls_mmock = MagicMock()
        cls_mmock.pull_from.return_value = False
        with patch.object(PoolSsh, 'get_node', return_value=cls_mmock):
            result = pull(request)
            self.assertTrue(result['result'])
            self.assertIsNone(result['error'])

        request.dbsession = AlchemyMagicMock()
        exception_mock = OperationalError(None, None, 'database timeout')
        request.dbsession.query = Mock()
        request.dbsession.query.side_effect = exception_mock
        request.dbsession.query.raiseError.side_effect = exception_mock
        result = pull(request)
        self.assertFalse(result['result'],)
        self.assertEqual(result['error'], 'database timeout')

        request.dbsession = AlchemyMagicMock()
        exception_mock = Exception("standard error")
        request.dbsession.query = Mock()
        request.dbsession.query.side_effect = exception_mock
        request.dbsession.query.raiseError.side_effect = exception_mock
        result = pull(request)
        self.assertFalse(result['result'],)
        self.assertEqual(result['error'], 'standard error')
