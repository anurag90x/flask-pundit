import inspect
import flask
from functools import wraps
from helpers import dasherized_name


def verify_authorized(func):
    @wraps(func)
    def inner(*args, **kwargs):
        pundit = getattr(flask.current_app, 'extensions', {})\
            .get('flask_pundit')
        stack_top = pundit._get_stack_top()
        response = func(*args, **kwargs)
        if not getattr(stack_top, 'authorize_called', False):
            raise RuntimeError('''
            Failed to call authorize method
            but used verification decorator''')
        return response
    return inner


def verify_policy_scoped(func):
    @wraps(func)
    def inner(*args, **kwargs):
        pundit = getattr(flask.current_app, 'extensions', {})\
            .get('flask_pundit')
        stack_top = pundit._get_stack_top()
        response = func(*args, **kwargs)
        if not getattr(stack_top, 'policy_scope_called', False):
            raise RuntimeError('''
            Failed to call policy_scope method
            but used verification decorator''')
        return response
    return inner


class FlaskPundit(object):

    SCOPE_ACTION = 'scope'
    POLICY_SUFFIX = 'Policy'

    def __init__(self, app=None, policies_path='policies'):
        self.app = app
        self.policies_path = policies_path
        if app is not None:
            self.init_app(app, policies_path)

    def init_app(self, app):
        if not hasattr(app, 'extensions'):
            app.extensions = {}
        app.extensions['flask_pundit'] = self

    def _get_app(self):
        if self.app:
            return self.app
        if flask.current_app:
            return flask.current_app
        raise RuntimeError('''
            Need to initialize extension with an app or have app context''')

    def authorize(self, record, action=None, user=None, *args, **kwargs):
        """ Call this method from within a resource or
        a route to authorize a model instance
        """
        current_user = user or self._get_current_user()
        action = action or self._get_action_from_request()
        policy_clazz = self._get_policy_clazz(record)

        self._get_stack_top().authorize_called = True
        return getattr(
            policy_clazz(current_user, record), action
        )(*args, **kwargs)

    def policy_scope(self, scope, user=None, *args, **kwargs):
        """ Call this method from within a resource or
        a route to return a scoped version of a mdoel
        For example, blog posts only viewable by the admin's staff.
        """
        current_user = user or self._get_current_user()
        action = FlaskPundit.SCOPE_ACTION
        policy_clazz = self._get_policy_clazz(scope)

        self._get_stack_top().policy_scope_called = True
        return getattr(
            policy_clazz(current_user, scope), action
        )(*args, **kwargs)

    def _verify_authorized(self):
        stack_top = self._get_stack_top()
        return getattr(stack_top, 'authorize_called', False)

    def _verify_policy_scoped(self):
        stack_top = self._get_stack_top()
        return getattr(stack_top, 'policy_scope_called', False)

    def _get_current_user(self):
        return flask.g.get('user') or flask.g.get('current_user')

    def _get_policy_clazz(self, record):
        if record is None:
            raise RuntimeError('''
            Need to pass an object or class type as a record''')

        model_policy_clazz = self._get_policy_clazz_from_model(record)
        return model_policy_clazz if model_policy_clazz is not None else\
            self._get_policy_clazz_from_policy_module(record)

    def _get_policy_clazz_from_model(self, record):
        model = self._get_model_class(record)
        return getattr(model, '__policy_class__', None)

    def _get_policy_clazz_from_policy_module(self, record):
        model = self._get_model_class(record)
        model_name = getattr(model, '__name__')
        policy_clazz = getattr(self._get_policy_module(model_name),
                               model_name + FlaskPundit.POLICY_SUFFIX)
        return policy_clazz

    def _get_model_class(self, record):
        ''' Returns the model corresponding to a record.
        If record is an object i.e has a __class__ attr then returns
        the object's class else returns the record (which should be a class)
        '''
        if inspect.isclass(record):
            return record
        record_class = getattr(record, '__class__', None)
        if record_class is not None:
            return record_class

    def _get_policy_module(self, model_name):
        dasherized_model_name = dasherized_name(model_name)
        policy_clazz_path = '.'.join([self.policies_path,
                                      dasherized_model_name])
        policy_clazz_module = __import__(
            policy_clazz_path,
            fromlist=[dasherized_model_name + FlaskPundit.POLICY_SUFFIX],
        )
        return policy_clazz_module

    def _get_action_from_request(self):
        return flask.request.method.lower()

    def _get_stack_top(self):
        if flask._app_ctx_stack.top is not None:
            return flask._app_ctx_stack.top
        raise RuntimeError('No application context present')
