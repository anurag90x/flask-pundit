from flask_pundit import FlaskPundit
from mock import Mock, patch
from nose.tools import ok_, eq_, assert_raises
from unittest import TestCase

class TestFlaskPundit(TestCase):
    def setUp(self):
        self.pundit = FlaskPundit()


    @patch('flask_pundit.importlib')
    @patch('flask_pundit.flask')
    def test_authorize_with_record(self, flask, importlib):
        flask.configure_mock(**({ 'g':{'user': 'admin'}, 'request.method':'GET'}))
        policy_class_instance = Mock(get = lambda : True)
        policy_class = Mock(return_value = policy_class_instance)
        importlib.import_module.return_value = policy_class

        record_class = Mock(__name__ = 'Record')
        record = Mock(__class__ = record_class)
        ok_(self.pundit.authorize(record))

    @patch('flask_pundit.importlib')
    @patch('flask_pundit.flask')
    def test_authorize_with_record_and_action(self, flask, importlib):
        flask.configure_mock(**({ 'g':{'user': 'admin'}, 'request.method':'GET'}))
        policy_class_instance = Mock(index = lambda : False)
        policy_class = Mock(return_value = policy_class_instance)
        importlib.import_module.return_value = policy_class

        record_class = Mock(__name__ = 'Record')
        record = Mock(__class__ = record_class)
        ok_(self.pundit.authorize(record))

    @patch('flask_pundit.importlib')
    @patch('flask_pundit.flask')
    def test_authorize_with_record_and_action_and_user(self, flask, importlib):
        flask.configure_mock(**({ 'g':{'user': 'admin'}, 'request.method':'GET'}))
        policy_class_instance = Mock(get = lambda : True)
        policy_class = Mock(return_value = policy_class_instance)
        importlib.import_module.return_value = policy_class

        record_class = Mock(__name__ = 'Record')
        user = { 'id': 1, 'role': 'admin' }
        record = Mock(__class__ = record_class)
        ok_(self.pundit.authorize(record, user=user))
        ok_(policy_class_instance.called_once_with(record, user))

    @patch('flask_pundit.flask')
    def test_authorize_throws_error_for_missing_policy(self, flask):
        flask.configure_mock(**({ 'g':{'user': 'admin'}}))
        record_class = Mock(__name__ = 'Record')
        record = Mock(__class__ = record_class)
        assert_raises(ImportError, self.pundit.authorize, record)

    @patch('flask_pundit.importlib')
    @patch('flask_pundit.flask')
    def test_authorize_throws_error_for_missing_action(self, flask, importlib):
        flask.configure_mock(**({ 'g':{'user': 'admin'}}))
        policy_class_instance = Mock(spec=['index'])
        policy_class = Mock(return_value = policy_class_instance)
        importlib.import_module.return_value = policy_class

        record_class = Mock(__name__ = 'Record')
        record = Mock(__class__ = record_class)
        assert_raises(AttributeError, self.pundit.authorize, record, 'update')

    @patch('flask_pundit.importlib')
    @patch('flask_pundit.flask')
    def test_policy_scope_triggers_resolve_action(self, flask, importlib):
        flask.configure_mock(**({ 'g':{'user': 'admin'}}))
        scope_class_instance = Mock(resolve = lambda : [1,2,3])
        scope_class = Mock(return_value=scope_class_instance)
        policy_class = Mock(Scope=scope_class)
        importlib.import_module.return_value = policy_class

        record_class = Mock(__name__ = 'Record')
        record = Mock(__class__ = record_class)
        eq_(self.pundit.policy_scope(record), [1,2,3])
