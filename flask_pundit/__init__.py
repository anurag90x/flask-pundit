from constants import PUNDIT_CALLBACKS
from flask import _app_ctx_stack as stack
import flask_pundit
from functools import wraps

authorize = flask_pundit.authorize
policy_scope = flask_pundit.policy_scope


def verify_authorized(func):
    @wraps(func)
    def inner(*args, **kwargs):
        stack.top[PUNDIT_CALLBACKS] = stack.top.get(PUNDIT_CALLBACKS, [])\
                                               .append(flask_pundit.verify_authorized)
        return func(*args, **kwargs)
    return inner


def verify_policy_scoped(func):
    @wraps(func)
    def inner(*args, **kwargs):
        stack.top[PUNDIT_CALLBACKS] = stack.top.get(PUNDIT_CALLBACKS, [])\
                                               .append(flask_pundit.verify_policy_scoped)
        return func(*args, **kwargs)
    return inner


@app.after_request
def _process_verification_callbacks():
    callbacks = stack.top.get(PUNDIT_CALLBACKS)
    for call in callbacks:
        if not call():
            raise RuntimeError
