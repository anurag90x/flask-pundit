import constants
import flask

from functools import wraps


def verify_authorized(func):
    @wraps(func)
    def inner(*args, **kwargs):
        pundit = getattr(flask.current_app, 'extensions', {}).get('flask_pundit')
        stack_top = pundit._get_stack_top()
        stack_top.pundit_callbacks = getattr(stack_top, 'pundit_callbacks', [])
        stack_top.pundit_callbacks.append(pundit._verify_authorized)
        return func(*args, **kwargs)
    return inner

def verify_policy_scoped(func):
    @wraps(func)
    def inner(*args, **kwargs):
        pundit = getattr(flask.current_app, 'extensions', {}).get('flask_pundit')
        stack_top = pundit._get_stack_top()
        stack_top.pundit_callbacks = getattr(stack_top, 'pundit_callbacks', [])
        stack_top.pundit_callbacks.append(pundit._verify_policy_scoped)
        return func(*args, **kwargs)
    return inner

def _process_verification_hooks(response):
    pundit = getattr(flask.current_app, 'extensions', {}).get('flask_pundit')
    stack_top = pundit._get_stack_top()
    callbacks = getattr(stack_top, 'pundit_callbacks', [])
    while len(callbacks) > 0:
        call = callbacks.pop()
        if call() is False:
            raise RuntimeError('''
            Failed to call authorize/policy_scope method
            but used verification decorator''')
    return response


class FlaskPundit(object):
    def __init__(self, app=None, policies_path='policies'):
        self.app = app
        self.policies_path = policies_path
        if app is not None:
            self.init_app(app, policies_path)

    def init_app(self, app):
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['flask_pundit'] = self
        app.after_request(_process_verification_hooks)

    def _get_app(self):
        if self.app:
            return self.app
        if flask.current_app:
            return flask.current_app
        raise RuntimeError('''
            Need to initialize extension with an app or have app context''')

    def authorize(self, record, action=None, user=None):
        """ Call this method from within a resource or
        a route to authorize a model instance
        """
        if record is None:
            raise RuntimeError('Need to pass a record object or model class')

        current_user = user or self._get_current_user()
        action = action or self._get_action_from_request()
        policy_clazz = self._get_policy_clazz(record)

        self._get_stack_top().authorize_called = True
        return getattr(policy_clazz(current_user, record), action)()

    def policy_scope(self, scope, user=None):
        """ Call this method from within a resource or
        For example, blog posts only viewable by the admin's staff.
        """
        if scope is None:
            raise RuntimeError('Need to pass a model class')

        current_user = user or self._get_current_user()
        action = constants.SCOPE_ACTION
        scope_clazz = self._get_scope_clazz(scope)

        if scope_clazz is None:
            raise RuntimeError('''
                Policy class is missing inner Scope class. Either
                inherit from ApplicationPolicy or create your own
                inner Scope class/ base policy class with an inner
                scope class definition ''')

        self._get_stack_top().policy_scope_called = True
        return getattr(scope_clazz(current_user, scope), action)()

    def _verify_authorized(self):
        stack_top = self._get_stack_top()
        return getattr(stack_top, 'authorize_called', False)

    def _verify_policy_scoped(self):
        stack_top = self._get_stack_top()
        return getattr(stack_top, 'policy_scope_called', False)

    def _get_current_user(self):
        return flask.g.get('user') or flask.g.get('current_user')

    def _get_policy_clazz(self, record):
        record_clazz_name = self._get_model_name(record)
        policy_clazz = getattr(self._get_policy_module(record_clazz_name),
                               record_clazz_name + 'Policy')
        return policy_clazz

    def _get_model_name(self, record):
        if getattr(record, '__class__', None):
            record_clazz_name = getattr(getattr(record, '__class__'), '__name__')
        else:
            record_clazz_name = getattr(record, '__name__')
        return record_clazz_name

    def _get_scope_clazz(self, record):
        policy_clazz = self._get_policy_clazz(record)
        return getattr(policy_clazz, 'Scope')

    def _get_policy_module(self, record_clazz_name):
        policy_clazz_path = '.'.join([self.policies_path,
                                      record_clazz_name.lower()])
        policy_clazz_module = __import__(policy_clazz_path,
                                         fromlist=[record_clazz_name + 'Policy'],
                                         )
        return policy_clazz_module

    def _get_action_from_request(self):
        return flask.request.method.lower()

    def _get_stack_top(self):
        if flask._app_ctx_stack.top is not None:
            return flask._app_ctx_stack.top
        raise RuntimeError('No application context present')
