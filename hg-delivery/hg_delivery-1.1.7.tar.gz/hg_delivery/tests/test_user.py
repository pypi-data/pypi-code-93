from pyramid.httpexceptions import HTTPBadRequest
from . import BasicDataIgnition
import transaction
from mock import MagicMock, Mock
from mock_alchemy.mocking import AlchemyMagicMock
from pyramid import testing
from sqlalchemy.exc import OperationalError
from datetime import datetime

# ------------------------------------------------------------------------------


class TestUser(BasicDataIgnition):

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

        self.users_list = self._add_some_user()

    def test_add_user(self):
        """
            test dummy view
        """
        from ..views import add_user

        request = testing.DummyRequest()
        settings_mock = MagicMock()
        request.registry.settings = settings_mock
        settings_dict = {'hg_delivery.default_login': 'editor'}
        settings_mock.__getitem__.side_effect = settings_dict.__getitem__
        request.dbsession = self.session

        # macro that pushes data from 1 to 2
        result = add_user(request)
        self.assertIsInstance(result, HTTPBadRequest)
        lb = 'Your user profile should contain a valid name'
        self.assertEqual(result.detail, lb)

        request.params['name'] = 'testMyName'
        result = add_user(request)
        self.assertIsInstance(result, HTTPBadRequest)
        lb = 'Your user profile should contain a valid email'
        self.assertEqual(result.detail, lb)

        request.params['email'] = 'test@free.fr'
        result = add_user(request)
        self.assertIsInstance(result, HTTPBadRequest)
        lb = "Your user profile musn't be empty"
        self.assertEqual(result.detail, lb)

        request.params['pwd'] = 'test'
        result = add_user(request)
        self.assertIsInstance(result, dict)
        self.assertTrue(result['result'])

        # insert twice to trigger integrity error
        result = add_user(request)
        self.assertIsInstance(result, HTTPBadRequest)
        lb = 'This user and this email are already'
        lb += ' defined (testMyName test@free.fr) ...'
        self.assertEqual(result.detail, lb)

        request.params['name'] = 'testMyName2'
        request.dbsession = AlchemyMagicMock()
        exception_mock = OperationalError(None, None, 'database timeout')
        request.dbsession.add = Mock()
        request.dbsession.add.side_effect = exception_mock
        request.dbsession.add.raiseError.side_effect = exception_mock
        result = add_user(request)
        self.assertIsInstance(result, HTTPBadRequest)
        self.assertEqual(result.detail, 'database timeout')

    def test_add_admin_user(self):
        """
            test dummy view
        """
        from ..views import add_user
        from ..models.hgd_model import User

        request = testing.DummyRequest()
        request.dbsession = self.session
        # Sets authenticated_userid
        self.config.testing_securitypolicy(userid='editor', permissive=True)

        request.user = User('editor', 'editor', 'editor')
        # Sets authenticated_userid
        self.config.testing_securitypolicy(userid='editor', permissive=True)
        settings_mock = MagicMock()
        request.registry.settings = settings_mock
        settings_dict = {'hg_delivery.default_login': 'editor@free.fr'}
        settings_mock.__getitem__.side_effect = settings_dict.__getitem__
        request.params['name'] = 'editor'
        request.params['email'] = 'editor@free.fr'
        result = add_user(request)
        self.assertIsInstance(result, HTTPBadRequest)
        lb = 'Your user profile should contain a valid email'
        self.assertEqual(result.detail, lb)

    def test_manage_users(self):
        """
            test dummy view
        """
        from ..views import manage_users
        from ..models.hgd_model import Acl, User
        p1, p2 = self._add_some_projects()
        default_user = self.users_list[0]

        request = testing.DummyRequest()

        request.dbsession = AlchemyMagicMock()
        exception_mock = OperationalError(None, None, 'database timeout')
        request.dbsession.query = Mock()
        request.dbsession.query.side_effect = exception_mock
        request.dbsession.query.raiseError.side_effect = exception_mock
        result = manage_users(request)
        self.assertFalse(result['result'])
        self.assertEqual(result['error'], 'database timeout')

        request = testing.DummyRequest()
        request.dbsession = self.session
        request.dbsession.add(Acl(default_user.id, p1.id, 'edit'))
        request.dbsession.flush()
        result = manage_users(request)
        self.assertTrue(result['result'])
        self.assertIsNone(result['error'])
        self.assertIsInstance(result['lst_users'], list)
        self.assertEqual(len(result['lst_users']), 1)
        self.assertIsInstance(result['lst_users'][0], User)
        self.assertEqual(len(result['known_acls']), 2)
        self.assertEqual(result['known_acls'][0], 'edit')
        self.assertEqual(result['known_acls'][1], 'read')

    def test_delete_user(self):
        """
        """
        from ..views import delete_user
        from ..models import User
        from pyramid.httpexceptions import HTTPFound, HTTPError
        from pyramid.httpexceptions import HTTPServerError

        # adding routes is necessary for testing ...
        self.config.add_route('users', '/users')

        # correct behavior
        request = testing.DummyRequest()
        request.dbsession = self.session
        default_user = self.users_list[0]
        request.matchdict['id'] = default_user.id
        result = delete_user(request)
        self.assertIsInstance(result, HTTPFound)

        user_count = self.session.query(User).count()
        self.assertEqual(user_count, 0)

        # no parameter
        request = testing.DummyRequest()
        request.dbsession = self.session
        result = delete_user(request)
        self.assertIsInstance(result, HTTPError)

        # sql error on query
        self._add_some_user()
        user = self.session.query(User).first()
        request = testing.DummyRequest()
        request.matchdict['id'] = user.id
        request.dbsession = AlchemyMagicMock()
        exception_mock = OperationalError(None, None, 'database timeout')
        request.dbsession.query = Mock()
        request.dbsession.query.side_effect = exception_mock
        request.dbsession.query.raiseError.side_effect = exception_mock
        result = delete_user(request)
        self.assertIsInstance(result, HTTPServerError)

        # sql error on delete
        user = self.session.query(User).first()
        request = testing.DummyRequest()
        request.matchdict['id'] = user.id
        request.dbsession = AlchemyMagicMock()
        exception_mock = OperationalError(None, None, 'database timeout')
        request.dbsession.delete = Mock()
        request.dbsession.delete.side_effect = exception_mock
        request.dbsession.delete.raiseError.side_effect = exception_mock
        result = delete_user(request)
        self.assertIsInstance(result, HTTPServerError)

        # no id found
        # just dissmiss error ?

    def test_get_users(self):
        """
        """
        from ..views import get_user
        from ..models import User

        # parameter error
        request = testing.DummyRequest()
        request.dbsession = self.session
        result = get_user(request)
        self.assertFalse(result['result'])
        self.assertEqual(result['error'], 'Bad parameter')
        self.assertIsNone(result['user'])

        # standard use case
        request = testing.DummyRequest()
        request.dbsession = self.session
        default_user = self.users_list[0]
        request.matchdict['id'] = default_user.id
        result = get_user(request)
        self.assertTrue(result['result'])
        self.assertIsNone(result['error'])
        self.assertIsNotNone(result['user'])
        self.assertIsInstance(result['user'], User)
        self.assertEqual(result['user'].id, default_user.id)

        # db error
        request.dbsession = AlchemyMagicMock()
        exception_mock = OperationalError(None, None, 'database timeout')
        request.dbsession.query = Mock()
        request.dbsession.query.side_effect = exception_mock
        request.dbsession.query.raiseError.side_effect = exception_mock
        result = get_user(request)
        self.assertFalse(result['result'])
        self.assertEqual(result['error'], 'database timeout')
        self.assertIsNone(result['user'])

    def test_update_user(self):
        """ """
        from ..views import update_user
        from ..models import User
        default_user = self.users_list[0]

        # default behavior
        request = testing.DummyRequest()
        request.dbsession = self.session
        request.matchdict['id'] = default_user.id
        request.params['name'] = 'new_name'
        request.params['email'] = 'new_email@world.fr'
        result = update_user(request)
        self.assertTrue(result['result'])
        lb = 'This user : new_name (new_email@world.fr) has been updated ...'
        self.assertEqual(result['explanation'], lb)

        # integrity error
        second_user = User('test', 'test', 'test2@france.fr', datetime.now())
        self.session.add(second_user)
        request = testing.DummyRequest()
        request.dbsession = self.session
        request.matchdict['id'] = default_user.id
        request.params['name'] = 'new_name'
        request.params['email'] = 'test2@france.fr'
        result = update_user(request)
        self.assertFalse(result['result'])
        lb = "You can't update this user, this email is"
        lb += " already used (new_name test2@france.fr) ..."
        self.assertEqual(result['explanation'], lb)

        # bad parameters
        request = testing.DummyRequest()
        request.dbsession = self.session
        request.params['name'] = 'new_name'
        request.params['email'] = 'new_email@world.fr'
        result = update_user(request)
        self.assertFalse(result['result'])
        self.assertEqual(result['explanation'], 'Bad parameter')

        request = testing.DummyRequest()
        request.dbsession = self.session
        request.matchdict['id'] = default_user.id
        request.params['email'] = 'new_email@world.fr'
        result = update_user(request)
        self.assertFalse(result['result'])
        self.assertEqual(result['explanation'], 'Bad parameter')

        request = testing.DummyRequest()
        request.dbsession = self.session
        request.matchdict['id'] = default_user.id
        request.params['name'] = 'new_name'
        result = update_user(request)
        self.assertFalse(result['result'])
        self.assertEqual(result['explanation'], 'Bad parameter')

        # unknown user
        request = testing.DummyRequest()
        request.dbsession = self.session
        request.matchdict['id'] = 42
        request.params['name'] = 'new_name'
        request.params['email'] = 'new_email@world.fr'
        result = update_user(request)
        self.assertFalse(result['result'])
        lb = 'This user is unknown or has already been deleted'
        self.assertEqual(result['explanation'], lb)

        # db error with mock
        request = testing.DummyRequest()
        request.dbsession = self.session
        request.matchdict['id'] = 42
        request.params['name'] = 'new_name'
        request.params['email'] = 'new_email@world.fr'
        exception_mock = OperationalError(None, None, 'database timeout')
        request.dbsession = self.session
        request.dbsession.query = Mock()
        request.dbsession.query.side_effect = exception_mock
        request.dbsession.query.raiseError.side_effect = exception_mock
        result = update_user(request)
        self.assertFalse(result['result'])
        self.assertTrue(result['explanation'].count('database timeout'))

        # db error standard exception with mock
        request = testing.DummyRequest()
        request.dbsession = self.session
        request.matchdict['id'] = 42
        request.params['name'] = 'new_name'
        request.params['email'] = 'new_email@world.fr'

        exception_mock = Exception('standard error')
        request.dbsession = self.session
        request.dbsession.query = Mock()
        request.dbsession.query.side_effect = exception_mock
        request.dbsession.query.raiseError.side_effect = exception_mock

        result = update_user(request)
        self.assertFalse(result['result'])
        self.assertEqual(result['explanation'], 'standard error')

        exception_mock = OperationalError(None, None, 'database timeout')
        request.dbsession = self.session
        request.dbsession.query = Mock()
        request.dbsession.query.side_effect = exception_mock
        request.dbsession.query.raiseError.side_effect = exception_mock
        result = update_user(request)
        self.assertFalse(result['result'])
        self.assertTrue(result['explanation'].count('database timeout'))
