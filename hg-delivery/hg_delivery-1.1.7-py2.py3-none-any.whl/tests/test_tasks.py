from . import BasicDataIgnition
import unittest
from sqlalchemy import exc
import transaction
from mock import MagicMock, Mock, patch, NonCallableMagicMock
from mock_alchemy.mocking import AlchemyMagicMock
from pyramid import testing
from sqlalchemy.exc import IntegrityError, OperationalError
from pyramid.testing import (setUp, tearDown, DummyRequest)

#------------------------------------------------------------------------------

class TestViewtasks(BasicDataIgnition):

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


    def test_view_all_tasks_standard_user(self):
        """
            no logs
            view returns an empty list of logs embed in a dict
            (json security)
        """
        from ..views import view_all_tasks
        from ..models.hgd_model import Task, Acl

        # empty tasks list
        request = testing.DummyRequest()
        default_user = self.users_list[0]
        request.user = default_user
        self.config.testing_securitypolicy(userid='editor', permissive=True)  # Sets authenticated_userid
        request.registry = MagicMock()
        request.registry.return_value.settings.return_value = {'hg_delivery.default_login':'editor'}
        request.dbsession = self.session
        result = view_all_tasks(request)
        self.assertTrue(result['result'])
        self.assertEqual(len(result['dict_project_to_tasks']), 0)

        # empty tasks list bc of ACl missing
        request = testing.DummyRequest()
        request.user = default_user 
        self.config.testing_securitypolicy(userid='editor', permissive=True)  # Sets authenticated_userid
        request.registry = MagicMock()
        request.registry.return_value.settings.return_value = {'hg_delivery.default_login':'editor'}
        request.dbsession = self.session
        p1,p2 = self.projects_list
        self.session.add(Task(p1.id, 'ls -al'))
        self.session.flush()
        result = view_all_tasks(request)
        self.assertTrue(result['result'])
        self.assertEqual(len(result['dict_project_to_tasks']), 0)

        # none empty tasks list
        request = testing.DummyRequest()
        request.user = default_user 
        self.config.testing_securitypolicy(userid='editor', permissive=True)  # Sets authenticated_userid
        request.registry = MagicMock()
        request.registry.return_value.settings.return_value = {'hg_delivery.default_login':'editor'}
        request.dbsession = self.session
        p1,p2 = self.projects_list
        self.session.add(Task(p1.id, 'ls -al'))
        request.dbsession.add(Acl(default_user.id, p1.id, 'edit'))
        self.session.flush()
        result = view_all_tasks(request)
        self.assertTrue(result['result'])
        self.assertEqual(len(result['dict_project_to_tasks']), 1)

    def test_view_all_tasks_admin(self):
        """
            no logs
            view returns an empty list of logs embed in a dict
            (json security)
        """
        from ..views import view_all_tasks
        from ..models.hgd_model import User

        request = testing.DummyRequest()
        request.user = User('editor', 'editor', 'editor')
        self.config.testing_securitypolicy(userid='editor', permissive=True)  # Sets authenticated_userid
        settings_mock = MagicMock()
        request.registry.settings = settings_mock
        settings_dict = {'hg_delivery.default_login':'editor'}
        settings_mock.__getitem__.side_effect = settings_dict.__getitem__
        request.dbsession = self.session
        result = view_all_tasks(request)
        self.assertTrue(result['result'])
        self.assertEqual(len(result['dict_project_to_tasks']), 0)

    def test_view_all_tasks_exception(self):
        """
            no logs
            view returns an empty list of logs embed in a dict
            (json security)
        """
        from ..views import view_all_tasks
        from ..models.hgd_model import User

        request = testing.DummyRequest()
        request.user = self.users_list[0]
        self.config.testing_securitypolicy(userid='editor', permissive=True)  # Sets authenticated_userid
        request.registry = MagicMock()
        request.registry.return_value.settings.return_value = {'hg_delivery.default_login':'editor'}
        request.dbsession = self.session
        exception_mock = OperationalError(None, None, 'database timeout')
        request.dbsession.query = Mock()
        request.dbsession.query.side_effect = exception_mock
        request.dbsession.query.raiseError.side_effect = exception_mock
        result = view_all_tasks(request)
        self.assertEqual(result['error'], 'database timeout')
        self.assertFalse(result['result'])
        self.assertEqual(len(result['dict_project_to_tasks']), 0)

        request = testing.DummyRequest()
        request.user = self.users_list[0]
        self.config.testing_securitypolicy(userid='editor', permissive=True)  # Sets authenticated_userid
        request.registry = MagicMock()
        request.registry.return_value.settings.return_value = {'hg_delivery.default_login':'editor'}
        request.dbsession = self.session
        exception_mock = Exception('standard exception')
        request.dbsession.query = Mock()
        request.dbsession.query.side_effect = exception_mock
        request.dbsession.query.raiseError.side_effect = exception_mock
        result = view_all_tasks(request)
        self.assertEqual(result['error'], 'standard exception')
        self.assertFalse(result['result'])
        self.assertEqual(len(result['dict_project_to_tasks']), 0)


    def test_view_all_tasks_parameters(self):
        from ..views import remove_project_task
        from ..models.hgd_model import Task, Acl

        # missing parameter
        request = testing.DummyRequest()
        default_user = self.users_list[0]
        request.user = default_user 
        self.config.testing_securitypolicy(userid='editor', permissive=True)  # Sets authenticated_userid
        request.registry = MagicMock()
        request.registry.return_value.settings.return_value = {'hg_delivery.default_login':'editor'}
        request.dbsession = self.session
        p1,p2 = self.projects_list
        task = Task(p1.id, 'ls -al')
        self.session.add(task)
        request.dbsession.add(Acl(default_user.id, p1.id, 'edit'))
        result = remove_project_task(request)
        self.assertFalse(result['result'])

        # parameter fullfilled
        request = testing.DummyRequest()
        default_user = self.users_list[0]
        request.user = default_user 
        self.config.testing_securitypolicy(userid='editor', permissive=True)  # Sets authenticated_userid
        request.registry = MagicMock()
        request.registry.return_value.settings.return_value = {'hg_delivery.default_login':'editor'}
        request.dbsession = self.session
        p1,p2 = self.projects_list
        task = Task(p1.id, 'ls -al')
        self.session.add(task)
        request.dbsession.add(Acl(default_user.id, p1.id, 'edit'))
        self.session.flush()
        request.matchdict['id'] = task.id
        result = remove_project_task(request)
        self.assertTrue(result['result'])

        # raising exception
        # SQL Alchemy error
        request = testing.DummyRequest()
        default_user = self.users_list[0]
        request.user = default_user 
        self.config.testing_securitypolicy(userid='editor', permissive=True)  # Sets authenticated_userid
        request.registry = MagicMock()
        request.registry.return_value.settings.return_value = {'hg_delivery.default_login':'editor'}
        request.dbsession = self.session
        p1,p2 = self.projects_list
        task = Task(p1.id, 'ls -al')
        self.session.add(task)
        request.dbsession.add(Acl(default_user.id, p1.id, 'edit'))
        self.session.flush()
        request.matchdict['id'] = task.id
        exception_mock = OperationalError(None, None, 'database timeout')
        request.dbsession.query = Mock()
        request.dbsession.query.side_effect = exception_mock
        request.dbsession.query.raiseError.side_effect = exception_mock
        result = remove_project_task(request)
        self.assertFalse(result['result'])

        # Integrity Error
        request = testing.DummyRequest()
        default_user = self.users_list[0]
        request.user = default_user 
        self.config.testing_securitypolicy(userid='editor', permissive=True)  # Sets authenticated_userid
        request.registry = MagicMock()
        request.registry.return_value.settings.return_value = {'hg_delivery.default_login':'editor'}
        request.dbsession = self.session
        p1,p2 = self.projects_list
        task = Task(p1.id, 'ls -al')
        self.session.add(task)
        request.dbsession.add(Acl(default_user.id, p1.id, 'edit'))
        self.session.flush()
        request.matchdict['id'] = task.id
        exception_mock = IntegrityError(None, None, 'database timeout')
        request.dbsession.query = Mock()
        request.dbsession.query.side_effect = exception_mock
        request.dbsession.query.raiseError.side_effect = exception_mock
        result = remove_project_task(request)
        self.assertFalse(result['result'])
        self.assertEqual(result['error'], 'database timeout')

        # Standard Exception
        request = testing.DummyRequest()
        default_user = self.users_list[0]
        request.user = default_user 
        self.config.testing_securitypolicy(userid='editor', permissive=True)  # Sets authenticated_userid
        request.registry = MagicMock()
        request.registry.return_value.settings.return_value = {'hg_delivery.default_login':'editor'}
        request.dbsession = self.session
        p1,p2 = self.projects_list
        task = Task(p1.id, 'ls -al')
        self.session.add(task)
        request.dbsession.add(Acl(default_user.id, p1.id, 'edit'))
        self.session.flush()
        request.matchdict['id'] = task.id
        exception_mock = Exception('standard error')
        request.dbsession.query = Mock()
        request.dbsession.query.side_effect = exception_mock
        request.dbsession.query.raiseError.side_effect = exception_mock
        result = remove_project_task(request)
        self.assertFalse(result['result'])
        self.assertEqual(result['error'], 'standard error')

    def tearDown(self):
        transaction.abort()
        testing.tearDown()
