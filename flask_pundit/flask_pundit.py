import flask

def authorize(record, action=None, user=None):
    """ Call this method from within a resource or
    a route to authorize a model instance
    """
    current_user = user or _get_current_user()
    action = action or _get_action_from_request()
    policy_clazz = _get_policy_clazz(record)
    return _delegate_action(policy_clazz, current_user, record, action)

def policy_scope(record, user=None):
    """ Call this method from within a resource or
    a route to return a 'scoped' version of a model.
    For example, blog posts only viewable by the admin's staff.
    """
    current_user = user or _get_current_user()
    action = 'resolve'
    scope_clazz = _get_scope_clazz(record)
    return _delegate_action(scope_clazz, current_user, record, action)

def _delegate_action(clazz, user, record, action):
    """ Delegates the action to an instance of the class
    that is passed in. This is either a policy class or
    the inner Scope class
    """
    if clazz is not None:
        return getattr(clazz(user, record), action)()
    raise RuntimeError('Required policy class for type %s' % record)

def _get_current_user():
    return flask.g.get('user') or flask.g.get('current_user')

def _get_policy_clazz(record):
    record_clazz = getattr(record, '__class__')
    return getattr(record_clazz, 'policy_class') if record_clazz else None

def _get_scope_clazz(record):
    policy_clazz = _get_policy_clazz(record)
    return getattr(policy_clazz, 'Scope') if policy_clazz else None

def _get_action_from_request():
    return flask.request.method.lower()
