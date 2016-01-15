from flask import g, Flask
from flask_pundit import FlaskPundit, verify_authorized
from models.user import User
from models.post import Post
from nose.tools import *
from unittest import TestCase


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
            return  self.pundit.authorize(post)

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

    def test_authorize_with_record_for_staff(self):
        def do_authorize_stuff():
            post = Post(1)
            return  self.pundit.authorize(post)

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

    def test_verify_authorized_decorator_success(self):
        def do_authorize_stuff():
            post = Post(1)
            return  self.pundit.authorize(post)

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
            return  self.pundit.authorize(post)

        @self.app.route('/test_authorize_admin_get')
        @verify_authorized
        def admin_get_post():
            g.user = {'id': 1, 'role': 'admin'}
            return 'Success', 200
        resp = self.client.get('/test_authorize_admin_get')
        eq_(resp.status_code, 200)
