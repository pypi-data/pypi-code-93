from . import BasicDataIgnition
import transaction
from mock import Mock
from mock_alchemy.mocking import AlchemyMagicMock
from pyramid import testing
from sqlalchemy.exc import OperationalError


# ------------------------------------------------------------------------------


class TestViewLogs(BasicDataIgnition):

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
        self.projects_list = self._add_some_projects()

    def tearDown(self):
        transaction.abort()
        testing.tearDown()

    def test_project_empty_logs(self):
        """
            no logs
            view returns an empty list of logs embed in a dict
            (json security)
        """
        from ..views import project_logs
        request = testing.DummyRequest()
        request.dbsession = self.session

        request.matchdict['id'] = 1
        info = project_logs(request)
        self.assertIsInstance(info['logs'], list)
        self.assertEqual(len(info['logs']), 0)

    def test_logs(self):
        """
            some valid logs (no project involved)
            no parameters for that view
        """
        from ..views import logs
        request = testing.DummyRequest()
        request.dbsession = self.session
        self._add_some_logs(count=1)
        info = logs(request)
        self.assertIsInstance(info['logs'], list)
        self.assertEqual(len(info['logs']), 2)
        self.assertEqual(info['logs'][0].command, 'ls -al')
        self.assertEqual(info['logs'][1].command, 'ls -al')

    def test_logs_mock(self):
        """
           test we could mock sqlalchemy query returns
        """
        from ..views import logs
        request = testing.DummyRequest()
        request.dbsession = AlchemyMagicMock()
        request.dbsession.execute.return_value.fetchall.return_value = []
        info = logs(request)
        self.assertEqual(len(info['logs']), 0)

    def test_logs_mock_db_exception(self):
        """
            test if database is gone
        """
        from ..views import logs
        request = testing.DummyRequest()
        request.dbsession = AlchemyMagicMock()
        exception_mock = OperationalError(None, None, 'database timeout')
        request.dbsession.query = Mock()
        request.dbsession.query.side_effect = exception_mock
        request.dbsession.query.raiseError.side_effect = exception_mock
        info = logs(request)
        self.assertEqual(len(info['logs']), 0)
        self.assertEqual(info['error'], 'database timeout')

        request = testing.DummyRequest()
        request.dbsession = AlchemyMagicMock()
        exception_mock = Exception("Default exception")
        request.dbsession.query = Mock()
        request.dbsession.query.side_effect = exception_mock
        request.dbsession.query.raiseError.side_effect = exception_mock
        info = logs(request)
        self.assertEqual(len(info['logs']), 0)
        self.assertEqual(info['error'], 'Default exception')

    def test_project_logs(self):
        """
            some valid logs per project
        """
        from ..views import project_logs
        self._add_some_logs(count=1)
        request = testing.DummyRequest()
        request.dbsession = self.session

        request.matchdict['id'] = 1
        info = project_logs(request)
        self.assertIsInstance(info['logs'], list)
        self.assertEqual(len(info['logs']), 1)

        request.matchdict['id'] = 2
        info = project_logs(request)
        self.assertIsInstance(info['logs'], list)
        self.assertEqual(len(info['logs']), 1)

        request.matchdict['id'] = None
        info = project_logs(request)
        self.assertIsInstance(info['logs'], list)
        self.assertEqual(len(info['logs']), 0)

        request.matchdict['id'] = -1
        info = project_logs(request)
        self.assertIsInstance(info['logs'], list)
        self.assertEqual(len(info['logs']), 0)

        request = testing.DummyRequest()
        request.matchdict['id'] = 1
        request.dbsession = AlchemyMagicMock()
        exception_mock = OperationalError(None, None, 'database timeout')
        request.dbsession.query = Mock()
        request.dbsession.query.side_effect = exception_mock
        request.dbsession.query.raiseError.side_effect = exception_mock
        info = project_logs(request)
        self.assertEqual(len(info['logs']), 0)
        self.assertEqual(info['error'], 'database timeout')

        request = testing.DummyRequest()
        request.matchdict['id'] = 1
        request.dbsession = AlchemyMagicMock()
        exception_mock = Exception("standard error")
        request.dbsession.query = Mock()
        request.dbsession.query.side_effect = exception_mock
        request.dbsession.query.raiseError.side_effect = exception_mock
        info = project_logs(request)
        self.assertEqual(len(info['logs']), 0)
        self.assertEqual(info['error'], "standard error")

    def test_limits(self):
        """
            test 50 max limit
        """
        from ..views import project_logs, logs
        self._add_some_logs(count=65)
        request = testing.DummyRequest()
        request.dbsession = self.session

        request.matchdict['id'] = 1
        info = project_logs(request)
        self.assertIsInstance(info['logs'], list)
        self.assertEqual(len(info['logs']), 50)

        request = testing.DummyRequest()
        request.dbsession = self.session
        info = logs(request)
        self.assertIsInstance(info['logs'], list)
        self.assertEqual(len(info['logs']), 50)
