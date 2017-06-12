from flask_pundit import FlaskPundit
from tests.policies.post import PostPolicy
from mock import Mock, patch
from nose.tools import ok_, eq_, assert_raises
from unittest import TestCase


class TestFlaskPundit(TestCase):
    def setUp(self):
        self.pundit = FlaskPundit()

    def get_flask_defaults(self):
        return {'g': {'user': 'admin'}, 'request.method': 'GET'}

    @patch('flask_pundit.flask')
    def test_authorize_with_record(self, flask):
        flask.configure_mock(**(self.get_flask_defaults()))
        policy_class_instance = Mock(get=lambda: True)
        policy_class = Mock(return_value=policy_class_instance)
        self.pundit._get_policy_clazz = Mock(return_value=policy_class)
        ok_(self.pundit.authorize(Mock()))

    @patch('flask_pundit.flask')
    def test_authorize_with_record_and_action(self, flask):
        flask.configure_mock(**(self.get_flask_defaults()))
        policy_class_instance = Mock(index=lambda: False)
        policy_class = Mock(return_value=policy_class_instance)
        self.pundit._get_policy_clazz = Mock(return_value=policy_class)
        ok_(not self.pundit.authorize(Mock(), 'index'))

    @patch('flask_pundit.flask')
    def test_authorize_with_record_and_action_and_user(self, flask):
        flask.configure_mock(**(self.get_flask_defaults()))
        user = {'id': 1, 'role': 'admin'}

        policy_class_instance = Mock(get=lambda: True)
        policy_class = Mock(return_value=policy_class_instance)

        self.pundit._get_policy_clazz = Mock(return_value=policy_class)
        record = Mock()
        ok_(self.pundit.authorize(record, user=user))
        ok_(policy_class_instance.called_once_with(record, user))

    @patch('flask_pundit.flask')
    def test_authorize_raises_exception_missing_action(self, flask):
        flask.configure_mock(**(self.get_flask_defaults()))
        policy_class_instance = Mock(spec=['index'])
        policy_class = Mock(return_value=policy_class_instance)

        self.pundit._get_policy_clazz = Mock(return_value=policy_class)
        record = Mock()
        assert_raises(AttributeError, self.pundit.authorize, record, 'update')

    @patch('flask_pundit.flask')
    def test_policy_scope_triggers_scope_action(self, flask):
        flask.configure_mock(**(self.get_flask_defaults()))
        policy_class_instance = Mock(scope=lambda: [1, 2, 3])
        policy_class = Mock(return_value=policy_class_instance)

        self.pundit._get_policy_clazz = Mock(return_value=policy_class)
        eq_(self.pundit.policy_scope(Mock()), [1, 2, 3])

    def test_get_policy_clazz_raises_exception_record_none(self):
        assert_raises(RuntimeError, self.pundit._get_policy_clazz, None)

    def test_get_model_class_with_object(self):
        record_class = Mock(__name__='Record')
        record = Mock(__class__=record_class)
        eq_(self.pundit._get_model_class(record), record_class)

    def test_get_model_class_with_class(self):
        eq_(self.pundit._get_model_class(PostPolicy), PostPolicy)

    def test_get_model_class_with_child_class(self):
        class ChildPostPolicy(PostPolicy):
            pass
        eq_(self.pundit._get_model_class(ChildPostPolicy), ChildPostPolicy)

    def test_get_policy_clazz_from_model(self):
        self.pundit._get_model_class = Mock(
            return_value=Mock(__policy_class__=PostPolicy))
        eq_(self.pundit._get_policy_clazz_from_model(Mock()), PostPolicy)
