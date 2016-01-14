from flask import g, Flask
from flask_pundit import FlaskPundit
from models.user import User
from models.post import Post
from nose.tools import *
from mock import Mock, patch

app = Flask('test')
pundit = FlaskPundit(policies_path='tests.policies')
pundit.init_app(app)
app.debug = True
client = app.test_client()

def test_authorize_with_record():
    @app.route('/helloworld')
    def hello_world():
        g.user = {'user': {'id':1, 'role': 'admin'}}
        post = Post(1)
        is_authorized = pundit.authorize(post)
        if is_authorized:
            return 'Success', 200
        else:
            return 'Unauthorized', 403
    resp = client.get('/helloworld')
    eq_(resp.status_code, 200)
