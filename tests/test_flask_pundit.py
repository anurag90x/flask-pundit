from flask_pundit.flask_pundit import authorize, policy_scope
from mock import Mock, patch
from nose.tools import ok_, eq_, assert_raises

@patch('flask_pundit.flask_pundit.flask')
def test_authorize_with_record(flask):
    flask.configure_mock(**({ 'g':{'user': 'admin'}, 'request.method':'GET'}))
    policy_class_instance = Mock(get = lambda : True)
    policy_class = Mock(return_value = policy_class_instance)
    record_class = Mock(policy_class = policy_class)
    record = Mock(__class__ = record_class)
    ok_(authorize(record))

@patch('flask_pundit.flask_pundit.flask')
def test_authorize_with_record_and_action(flask):
    flask.configure_mock(**({ 'g':{'user': 'admin'}, 'request.method':'GET'}))
    policy_class_instance = Mock(index = lambda : False)
    policy_class = Mock(return_value = policy_class_instance)
    record_class = Mock(policy_class = policy_class)
    record = Mock(__class__ = record_class)
    ok_(not authorize(record, 'index'))

@patch('flask_pundit.flask_pundit.flask')
def test_authorize_with_record_and_action_and_user(flask):
    flask.configure_mock(**({ 'g':{'user': 'admin'}, 'request.method':'GET'}))
    policy_class_instance = Mock(get = lambda : True)
    policy_class = Mock(return_value = policy_class_instance)
    record_class = Mock(policy_class = policy_class)
    record = Mock(__class__ = record_class)
    user = { 'id': 1, 'role': 'admin' }
    ok_(authorize(record, user=user))
    ok_(policy_class_instance.called_once_with(record, user))

def test_authorize_throws_error_for_missing_policy():
    record_class = Mock(policy_class = None, __name__ = 'Record')
    record = Mock(__class__ = record_class)
    assert_raises(RuntimeError, authorize, record)

@patch('flask_pundit.flask_pundit.flask')
def test_authorize_throws_error_for_missing_action(flask):
    flask.configure_mock(**({ 'g':{'user': 'admin'}}))
    policy_class_instance = Mock(spec=['index'])
    policy_class = Mock(return_value = policy_class_instance)
    record_class = Mock(policy_class = policy_class)
    record = Mock(__class__ = record_class)
    assert_raises(AttributeError, authorize, record, 'update')

@patch('flask_pundit.flask_pundit.flask')
def test_policy_scope_triggers_resolve_action(flask):
    flask.configure_mock(**({ 'g':{'user': 'admin'}}))
    scope_class_instance = Mock(resolve = lambda : [1,2,3])
    scope_class = Mock(return_value=scope_class_instance)
    policy_class = Mock(Scope=scope_class)
    record_class = Mock(policy_class = policy_class)
    record = Mock(__class__ = record_class)
    eq_(policy_scope(record), [1,2,3])
