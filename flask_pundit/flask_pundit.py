import flask

def authorize(record, action=None, user=None):
    """ Call this method from within a resource or
    a route to authorize a model instance
    """
    current_user = user or _get_current_user()
    action = action or _get_action_from_request()
    policy_clazz = _get_policy_clazz(record)

    if policy_clazz is not None:
        return getattr(policy_clazz(current_user, record), action)()
    raise RuntimeError('Required policy class for type %s' % record)

def _get_current_user():
    return flask.g.get('user') or flask.g.get('current_user')

def _get_policy_clazz(record):
    record_clazz = getattr(record, '__class__')
    return getattr(record_clazz, 'policy_class') if record_clazz else None

def _get_action_from_request():
    return flask.request.method.lower()
