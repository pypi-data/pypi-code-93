from . import BasicDataIgnition
import transaction
from mock import MagicMock, Mock
from mock_alchemy.mocking import AlchemyMagicMock
from pyramid import testing
from unittest.mock import patch
from sqlalchemy.exc import IntegrityError, OperationalError


class TestMacro(BasicDataIgnition):

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

    def test_add_macro(self):
        """
            nominal test
        """
        from ..views import create_a_macro
        from ..models.hgd_model import Macro, MacroRelations
        p_1, p_2 = self._add_some_projects()

        request = testing.DummyRequest()
        request.dbsession = self.session

        # macro that pushes data from 1 to 2
        request.matchdict['id'] = p_1.id
        result = create_a_macro(request)
        self.assertFalse(result['result'])
        self.assertIsInstance(result['result'], bool)
        self.assertEqual(result['error'], 'macro label is mandatory')
        request.params['macro_name'] = 'My MACRO LABEL'
        request.params['direction_2'] = 'push'

        # if parameters are full filled, no error
        result = create_a_macro(request)
        self.assertTrue(result['result'])
        self.assertIsInstance(result['result'], bool)
        self.assertIsNone(result['error'])

        # check db
        nb_macro = self.session.query(Macro).count()
        self.assertEqual(nb_macro, 1)
        macro = self.session.query(Macro).first()
        self.assertEqual(macro.label, 'My MACRO LABEL')
        self.assertEqual(len(macro.relations), 1)
        self.assertEqual(macro.relations[0].id, p_1.id)

        request.matchdict['id'] = p_2.id
        request.params['macro_name'] = 'My MACRO LABEL 2'
        request.params['direction_2'] = 'pull'
        result = create_a_macro(request)
        self.assertTrue(result['result'])
        self.assertIsInstance(result['result'], bool)
        self.assertIsNone(result['error'])

        nb_macro = self.session.query(Macro).count()
        self.assertEqual(nb_macro, 2)
        macro = self.session.query(Macro).filter(Macro.id != macro.id).first()
        self.assertEqual(macro.label, 'My MACRO LABEL 2')
        self.assertEqual(len(macro.relations), 1)
        self.assertEqual(macro.relations[0].id, p_2.id)

        nb_relations = self.session.query(MacroRelations).count()
        self.assertEqual(nb_relations, 2)
        nb_macro = self.session.query(Macro).count()
        self.assertEqual(nb_macro, 2)

        request.dbsession = AlchemyMagicMock()
        exception_mock = OperationalError(None, None, 'database timeout')
        request.dbsession.query = Mock()
        request.dbsession.query.side_effect = exception_mock
        request.dbsession.query.raiseError.side_effect = exception_mock
        result = create_a_macro(request)
        self.assertFalse(result['result'])
        self.assertEqual(result['error'], 'database error')

    def test_add_macro_on_unknown_project(self):
        """
            nominal test
        """
        from ..views import create_a_macro
        from ..models.hgd_model import Macro, MacroRelations

        request = testing.DummyRequest()
        request.dbsession = self.session

        # test unknown project source
        request.matchdict['id'] = 42
        request.params['macro_name'] = 'My MACRO LABEL'
        request.params['direction_2'] = 'push'

        result = create_a_macro(request)
        self.assertFalse(result['result'])
        self.assertIsInstance(result['result'], bool)
        self.assertEqual(result['error'], 'source project is unknown')

        nb_relations = self.session.query(MacroRelations).count()
        self.assertEqual(nb_relations, 0)
        nb_macro = self.session.query(Macro).count()
        self.assertEqual(nb_macro, 0)

        p1, p2 = self._add_some_projects()
        request = testing.DummyRequest()
        request.dbsession = self.session

        # test unknown project targed
        request.matchdict['id'] = p1.id
        request.params['macro_name'] = 'My MACRO LABEL'
        request.params['direction_42'] = 'push'

        result = create_a_macro(request)
        self.assertFalse(result['result'])
        self.assertIsInstance(result['result'], bool)
        self.assertEqual(result['error'], 'aim project is unknown')

        nb_relations = self.session.query(MacroRelations).count()
        self.assertEqual(nb_relations, 0)
        nb_macro = self.session.query(Macro).count()
        self.assertEqual(nb_macro, 0)

        # test wrong format for the direction
        request.matchdict['id'] = p1.id
        request.params['macro_name'] = 'My MACRO LABEL 3'
        request.params['direction_2'] = 'wut'

        result = create_a_macro(request)
        self.assertFalse(result['result'])
        self.assertIsInstance(result['result'], bool)
        self.assertEqual(result['error'], 'wrong format')

        nb_relations = self.session.query(MacroRelations).count()
        self.assertEqual(nb_relations, 0)
        nb_macro = self.session.query(Macro).count()
        self.assertEqual(nb_macro, 0)

    def test_delete_macro(self):
        """
        """
        from ..views import create_a_macro, delete_a_macro
        from ..models.hgd_model import Macro, MacroRelations
        p_1, p_2 = self._add_some_projects()

        request = testing.DummyRequest()
        request.dbsession = self.session

        request.matchdict['id'] = p_1.id
        request.params['macro_name'] = 'My MACRO LABEL'
        request.params['direction_2'] = 'push'

        # create a macro and delete it
        result = create_a_macro(request)
        self.assertTrue(result['result'])
        self.assertIsInstance(result['result'], bool)
        self.assertIsNone(result['error'])
        first_macro_id = self.session.query(Macro).first().id

        request.matchdict['macro_id'] = first_macro_id
        result = delete_a_macro(request)
        self.assertTrue(result['result'])
        self.assertIsInstance(result['result'], bool)
        self.assertIsNone(result['error'])

        # check db content
        nb_relations = self.session.query(MacroRelations).count()
        self.assertEqual(nb_relations, 0)
        nb_macro = self.session.query(Macro).count()
        self.assertEqual(nb_macro, 0)

    def test_delete_unknown_macro(self):
        """
        """
        from ..views import delete_a_macro
        from ..models.hgd_model import Macro, MacroRelations

        request = testing.DummyRequest()
        request.dbsession = self.session

        request.matchdict['macro_id'] = 42
        result = delete_a_macro(request)
        self.assertFalse(result['result'])
        self.assertIsInstance(result['result'], bool)
        self.assertEqual(result['error'], 'Unable to delete macro')
        nb_relations = self.session.query(MacroRelations).count()
        self.assertEqual(nb_relations, 0)
        nb_macro = self.session.query(Macro).count()
        self.assertEqual(nb_macro, 0)

    def test_run_a_macro_no_authorization(self):
        """
        """
        from ..views import run_a_macro, create_a_macro
        user = self.users_list[0]

        p1, p2 = self._add_some_projects()

        request = testing.DummyRequest()
        request.dbsession = self.session
        request.matchdict['id'] = p1.id
        request.params['macro_name'] = 'My MACRO LABEL'
        request.params['direction_2'] = 'push'
        result = create_a_macro(request)

        request = testing.DummyRequest()
        request.dbsession = self.session
        request.matchdict['id'] = p1.id
        request.matchdict['macro_id'] = 1

        request.registry = MagicMock()
        d_conf = {'hg_delivery.default_login': 'editor'}
        request.registry.return_value.settings.return_value = d_conf
        request.user = user
        result = run_a_macro(request)
        self.assertFalse(result['new_branch_stop'])
        self.assertFalse(result['new_head_stop'])
        self.assertFalse(result['lst_new_branches'])

        self.assertIsInstance(result['project_errors'], list)
        self.assertEqual(len(result['project_errors']), 1)
        self.assertEqual(result['project_errors'][0], 'project2')

        self.assertIsInstance(result['buffers'], dict)
        self.assertEqual(len(result['buffers']), 1)
        self.assertEqual(result['buffers']['project2'],
                         "user don't have access to project2")

    def test_run_a_macro_not_authorized(self):
        from ..nodes import PoolSsh
        from ..models.hgd_model import Acl
        from ..views import run_a_macro, create_a_macro
        user = self.users_list[0]

        p1, p2 = self._add_some_projects()

        request = testing.DummyRequest()
        request.dbsession = self.session
        request.matchdict['id'] = p1.id
        request.params['macro_name'] = 'My MACRO LABEL'
        request.params['direction_2'] = 'push'
        result = create_a_macro(request)

        request = testing.DummyRequest()
        request.dbsession = self.session
        request.matchdict['id'] = p1.id
        request.matchdict['macro_id'] = 1

        # auth
        request.dbsession.add(Acl(user.id, p1.id, 'edit'))
        request.dbsession.add(Acl(user.id, p2.id, 'edit'))
        request.dbsession.flush()

        request.registry = MagicMock()
        d_conf = {'hg_delivery.default_login': 'editor'}
        request.registry.return_value.settings.return_value = d_conf
        request.user = user

        cls_mmock = MagicMock()
        returned_data = {'mock': 'ok'}
        cls_mmock.push_to.return_value = returned_data

        with patch.object(PoolSsh, 'get_node', return_value=cls_mmock):
            result = run_a_macro(request)
            self.assertTrue(result['result'])
            self.assertFalse(result['new_branch_stop'])
            self.assertFalse(result['new_head_stop'])
            self.assertEqual(str(result['data']), "{'mock': 'ok'}")

    def test_update_a_macro(self):
        """
        """
        from ..models.hgd_model import Macro, MacroRelations
        from ..views import update_a_macro

        p_1, p_2 = self._add_some_projects()

        request = testing.DummyRequest()
        request.dbsession = self.session

        # macro that pushes data from 1 to 2
        macro = Macro(p_1.id, 'macro test')
        self.session.add(macro)
        macro_relation = MacroRelations(p_2.id, 'push')
        request.dbsession.add(macro_relation)
        macro.relations.append(macro_relation)
        self.session.flush()
        id_macro = macro.id

        # missing parameter
        result = update_a_macro(request)
        self.assertFalse(result['result'])
        self.assertEqual(result['explanation'], 'bad parameter')

        # good behavior
        request.matchdict['macro_id'] = id_macro
        request.params['macro_name'] = 'My MACRO LABEL'
        request.params['direction_2'] = 'pull'
        result = update_a_macro(request)
        self.assertTrue(result['result'])
        self.assertIsNone(result['explanation'])

        # missing macro description, doesn't change anything
        request.matchdict['macro_id'] = id_macro
        result = update_a_macro(request)
        self.assertTrue(result['result'])
        self.assertIsNone(result['explanation'])
        # relations didn't change
        self.assertEqual(request.dbsession.query(MacroRelations).count(), 1)

        request.matchdict['macro_id'] = id_macro
        request.dbsession = AlchemyMagicMock()
        exception_mock = OperationalError(None, None, 'database timeout')
        request.dbsession.query = Mock()
        request.dbsession.query.side_effect = exception_mock
        request.dbsession.query.raiseError.side_effect = exception_mock
        result = update_a_macro(request)
        self.assertFalse(result['result'])
        self.assertEqual(result['explanation'], 'database timeout')

        request.matchdict['macro_id'] = id_macro
        request.dbsession = AlchemyMagicMock()
        exception_mock = IntegrityError(None, None, 'integrity error on table')
        request.dbsession.add = Mock()
        request.dbsession.add.side_effect = exception_mock
        request.dbsession.add.raiseError.side_effect = exception_mock
        result = update_a_macro(request)
        self.assertFalse(result['result'])
        lb = 'This macro has already been define  ...'
        self.assertEqual(result['explanation'], lb)

    def test_view_all_macros(self):
        """
        """
        from ..models.hgd_model import Acl, Macro, MacroRelations
        from ..views import view_all_macros

        # a user without Acl can't see macros

        # an administrator user can see macros

        # a user with Acl can see macros
        default_user = self.users_list[0]
        p_1, p_2 = self._add_some_projects()
        request = testing.DummyRequest()
        request.dbsession = self.session
        request.user = default_user

        # Sets authenticated_userid
        self.config.testing_securitypolicy(userid='editor', permissive=True)
        request.registry = MagicMock()
        d_conf = {'hg_delivery.default_login': 'editor'}
        request.registry.return_value.settings.return_value = d_conf
        macro = Macro(p_1.id, 'macro test')
        self.session.add(macro)
        macro_relation = MacroRelations(p_2.id, 'push')
        request.dbsession.add(macro_relation)
        macro.relations.append(macro_relation)
        request.dbsession.add(Acl(default_user.id, p_1.id, 'edit'))
        request.dbsession.add(Acl(default_user.id, p_2.id, 'edit'))
        request.dbsession.flush()
        self.session.flush()
        result = view_all_macros(request)
        self.assertEqual(len(result['dict_project_to_macros']), 1)
