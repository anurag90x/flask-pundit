from flask_pundit import FlaskPundit
from mock import Mock, patch
from nose.tools import ok_, eq_, assert_raises
from unittest import TestCase

class TestFlaskPundit(TestCase):
    def setUp(self):
        self.pundit = FlaskPundit()

    def get_flask_defaults(self):
        return { 'g':{'user': 'admin'}, 'request.method':'GET'}

    @patch('flask_pundit.flask')
    def test_authorize_with_record(self, flask):
        flask.configure_mock(**(self.get_flask_defaults()))
        policy_class_instance = Mock(get = lambda : True)
        policy_class = Mock(return_value = policy_class_instance)
        self.pundit._get_policy_clazz = Mock(return_value = policy_class)
        ok_(self.pundit.authorize(Mock()))

    @patch('flask_pundit.flask')
    def test_authorize_with_record_and_action(self, flask):
        flask.configure_mock(**(self.get_flask_defaults()))
        policy_class_instance = Mock(index = lambda : False)
        policy_class = Mock(return_value = policy_class_instance)
        self.pundit._get_policy_clazz = Mock(return_value = policy_class)
        ok_(not self.pundit.authorize(Mock(), 'index'))

    @patch('flask_pundit.flask')
    def test_authorize_with_record_and_action_and_user(self, flask):
        flask.configure_mock(**(self.get_flask_defaults()))
        user = { 'id': 1, 'role': 'admin' }

        policy_class_instance = Mock(get = lambda : True)
        policy_class = Mock(return_value = policy_class_instance)

        self.pundit._get_policy_clazz = Mock(return_value = policy_class)
        record = Mock()
        ok_(self.pundit.authorize(record, user=user))
        ok_(policy_class_instance.called_once_with(record, user))

    @patch('flask_pundit.flask')
    def test_authorize_throws_error_for_missing_action(self, flask):
        flask.configure_mock(**(self.get_flask_defaults()))
        policy_class_instance = Mock(spec=['index'])
        policy_class = Mock(return_value = policy_class_instance)

        self.pundit._get_policy_clazz = Mock(return_value = policy_class)
        record = Mock()
        assert_raises(AttributeError, self.pundit.authorize, record, 'update')

    @patch('flask_pundit.flask')
    def test_policy_scope_triggers_resolve_action(self, flask):
        flask.configure_mock(**(self.get_flask_defaults()))
        scope_class_instance = Mock(resolve = lambda : [1,2,3])
        scope_class = Mock(return_value=scope_class_instance)
        policy_class = Mock(Scope=scope_class)

        self.pundit._get_policy_clazz = Mock(return_value = policy_class)
        record = Mock()
        eq_(self.pundit.policy_scope(record), [1,2,3])
