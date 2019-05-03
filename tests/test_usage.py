from flask import g, Flask
from flask_pundit import (
    FlaskPundit,
    verify_authorized,
    verify_policy_scoped,
    verify_authorized_or_policy_scoped
)
from .models.post import Post
from .models.comment import Comment
from nose.tools import (
    assert_raises,
    ok_,
    eq_)
from unittest import TestCase
from werkzeug.exceptions import BadRequest
import json


class TestUsage(TestCase):
    def setUp(self):
        self.app = Flask('test')
        self.app.debug = True
        self.pundit = FlaskPundit(policies_path='tests.policies')
        self.pundit.init_app(self.app)
        self.client = self.app.test_client()

    def test_authorize_with_record_for_admin(self):
        def do_authorize_stuff():
            post = Post(1)
            return self.pundit.authorize(post)

        @self.app.route('/test_authorize_admin_get')
        def admin_get_post():
            g.user = {'id': 1, 'role': 'admin'}
            is_authorized = do_authorize_stuff()
            ok_(self.pundit._verify_authorized())
            if is_authorized:
                return 'Success', 200
            else:
                return 'Forbidden', 403
        resp = self.client.get('/test_authorize_admin_get')
        eq_(resp.status_code, 200)

    def test_authorize_with_record_for_admin_with_params(self):
        def do_authorize_stuff():
            post = Post(1)
            return self.pundit.authorize(post, thing_id=1)

        @self.app.route('/test_authorize_admin_get')
        def admin_get_post():
            g.user = {'id': 1, 'role': 'admin'}
            is_authorized = do_authorize_stuff()
            ok_(self.pundit._verify_authorized())
            if is_authorized:
                return 'Success', 200
            else:
                return 'Forbidden', 403
        resp = self.client.get('/test_authorize_admin_get')
        eq_(resp.status_code, 403)

    def test_authorize_with_record_for_staff(self):
        def do_authorize_stuff():
            post = Post(1)
            return self.pundit.authorize(post)

        @self.app.route('/test_authorize_staff_get')
        def admin_get_post():
            g.user = {'id': 2, 'role': 'staff'}
            is_authorized = do_authorize_stuff()
            ok_(self.pundit._verify_authorized())
            if is_authorized:
                return 'Success', 200
            else:
                return 'Forbidden', 403
        resp = self.client.get('/test_authorize_staff_get')
        eq_(resp.status_code, 403)

    def test_authorize_with_model_for_admin(self):
        def do_authorize_stuff():
            return self.pundit.authorize(Post, action='create')

        @self.app.route('/test_authorize_admin_create')
        def admin_create_post():
            g.user = {'id': 1, 'role': 'admin'}
            is_authorized = do_authorize_stuff()
            ok_(self.pundit._verify_authorized())
            if is_authorized:
                return 'Success', 200
            else:
                return 'Forbidden', 403
        resp = self.client.get('/test_authorize_admin_create')
        eq_(resp.status_code, 200)

    def test_authorize_with_policy_class_specified_for_admin(self):
        def do_authorize_stuff():
            return self.pundit.authorize(Comment)

        @self.app.route('/test_authorize_admin_get_comment')
        def admin_get_comment():
            g.user = {'id': 1, 'role': 'admin'}
            is_authorized = do_authorize_stuff()
            ok_(self.pundit._verify_authorized())
            if is_authorized:
                return 'Success', 200
            else:
                return 'Forbidden', 403
        resp = self.client.get('/test_authorize_admin_get_comment')
        eq_(resp.status_code, 200)

    def test_verify_authorized_decorator_success(self):
        def do_authorize_stuff():
            post = Post(1)
            return self.pundit.authorize(post)

        @self.app.route('/test_authorize_admin_get')
        @verify_authorized
        def admin_get_post():
            g.user = {'id': 1, 'role': 'admin'}
            is_authorized = do_authorize_stuff()
            if is_authorized:
                return 'Success', 200
            else:
                return 'Forbidden', 403
        resp = self.client.get('/test_authorize_admin_get')
        eq_(resp.status_code, 200)

    def test_verify_authorized_decorator_raises_exception(self):
        def do_authorize_stuff():
            post = Post(1)
            return self.pundit.authorize(post)

        @self.app.route('/test_authorize_admin_get')
        @verify_authorized
        def admin_get_post():
            g.user = {'id': 1, 'role': 'admin'}
            return 'Success', 200
        assert_raises(RuntimeError, self.client.get,
                      '/test_authorize_admin_get')

    def test_verify_authorized_decorator_ignores_raised_exception(self):
        def do_authorize_stuff():
            post = Post(1)
            return self.pundit.authorize(post)

        @self.app.route('/test_authorize_admin_get')
        @verify_authorized
        def admin_get_post():
            g.user = {'id': 1, 'role': 'admin'}
            raise BadRequest()
            is_authorized = do_authorize_stuff()
            if is_authorized:
                return 'Success', 200
            else:
                return 'Forbidden', 403
        resp = self.client.get('/test_authorize_admin_get')
        eq_(resp.status_code, 400)

    def test_policy_scoped_admin(self):
        def do_policy_scope_stuff():
            return self.pundit.policy_scope(Post)

        @self.app.route('/test_policy_scope_admin')
        def admin_get_post():
            g.user = {'id': 1, 'role': 'admin'}
            scoped_posts = do_policy_scope_stuff()
            ok_(self.pundit._verify_policy_scoped())
            return json.dumps({'posts': scoped_posts})
        resp = self.client.get('/test_policy_scope_admin')
        eq_(resp.data.decode(), '{"posts": [1, 2]}')

    def test_policy_scoped_staff(self):
        def do_policy_scope_stuff():
            return self.pundit.policy_scope(Post)

        @self.app.route('/test_policy_scope_staff')
        def admin_get_post():
            g.user = {'id': 2, 'role': 'staff'}
            scoped_posts = do_policy_scope_stuff()
            ok_(self.pundit._verify_policy_scoped())
            return json.dumps({'posts': scoped_posts})
        resp = self.client.get('/test_policy_scope_staff')
        eq_(resp.data.decode(), '{"posts": [3, 4]}')

    def test_policy_scope_with_policy_class_specified_for_admin(self):
        def do_policy_scope_stuff():
            return self.pundit.policy_scope(Comment)

        @self.app.route('/test_policy_scope_admin_get_comments')
        def admin_get_comments():
            g.user = {'id': 1, 'role': 'admin'}
            scoped_comments = do_policy_scope_stuff()
            ok_(self.pundit._verify_policy_scoped())
            return json.dumps({'comments': scoped_comments})
        resp = self.client.get('/test_policy_scope_admin_get_comments')
        eq_(resp.data.decode(), '{"comments": ["Hello"]}')

    def test_verify_policy_scoped_decorator_success(self):
        def do_policy_scope_stuff():
            return self.pundit.policy_scope(Post)

        @self.app.route('/test_policy_scope_admin')
        @verify_policy_scoped
        def admin_get_post():
            g.user = {'id': 1, 'role': 'admin'}
            scoped_posts = do_policy_scope_stuff()
            return json.dumps({'posts': scoped_posts})
        resp = self.client.get('/test_policy_scope_admin')
        eq_(resp.data.decode(), '{"posts": [1, 2]}')

    def test_verify_policy_scoped_decorator_raises_exception(self):
        def do_policy_scope_stuff():
            return self.pundit.policy_scope(Post)

        @self.app.route('/test_policy_scope_admin')
        @verify_policy_scoped
        def admin_get_post():
            g.user = {'id': 1, 'role': 'admin'}
            return json.dumps({'posts': []})
        assert_raises(RuntimeError, self.client.get,
                      '/test_policy_scope_admin')

    def test_verify_either_decorator_success_with_authorize(self):
        def do_authorize_stuff():
            post = Post(1)
            return self.pundit.authorize(post)

        @self.app.route('/test_authorize_admin_get')
        @verify_authorized_or_policy_scoped
        def admin_get_post():
            g.user = {'id': 1, 'role': 'admin'}
            raise BadRequest()
            is_authorized = do_authorize_stuff()
            if is_authorized:
                return 'Success', 200
            else:
                return 'Forbidden', 403
        resp = self.client.get('/test_authorize_admin_get')
        eq_(resp.status_code, 400)

    def test_verify_either_decorator_success_with_scope(self):
        def do_policy_scope_stuff():
            return self.pundit.policy_scope(Post)

        @self.app.route('/test_policy_scope_admin')
        @verify_authorized_or_policy_scoped
        def admin_get_post():
            g.user = {'id': 1, 'role': 'admin'}
            scoped_posts = do_policy_scope_stuff()
            return json.dumps({'posts': scoped_posts})
        resp = self.client.get('/test_policy_scope_admin')
        eq_(resp.data.decode(), '{"posts": [1, 2]}')

    def test_verify_either_decorator_raises_exception(self):
        def do_policy_scope_stuff():
            return self.pundit.policy_scope(Post)

        @self.app.route('/test_policy_scope_admin')
        @verify_authorized_or_policy_scoped
        def admin_get_post():
            g.user = {'id': 1, 'role': 'admin'}
            return json.dumps({'posts': []})
        assert_raises(RuntimeError, self.client.get,
                      '/test_policy_scope_admin')
