def authorize(record, action=get_action_from_request, user=get_current_user):
    current_user, action, policy_clazz = _get_parameters(user, action)
    if policy_clazz is not None:
        return getattr(policy_clazz(current_user, record), action)()
    else:
        raise RunTimeError('Required policy class for type %s' % record)

def get_current_user():
    return flask.g.get('user') or flask.g.get('current_user')

def get_policy_clazz(record):
    record_clazz = getattr(record, '__class__')
    if record_clazz:
        policy_clazz = getattr(record_clazz, 'policy_class')
        return policy_clazz

def get_action_from_request():
    return request.method.lower()

def _get_parameters(user, action):
    current_user = user if !has_attr(user, '__call__') else user()
    action = action if !has_attr(action, '__call__') else action()
    policy_clazz = get_policy_clazz()
    return (current_user, action, policy_clazz)
