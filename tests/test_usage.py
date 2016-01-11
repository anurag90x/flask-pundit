from flask import g, Flask
from flask_pundit.flask_pundit import authorize
from models import User, Post
from policies import PostPolicy
from nose.tools import *
from mock import Mock, patch

app = Flask('test')
app.debug = True
client = app.test_client()

@patch.object(PostPolicy, 'get', lambda self: True)
def test_authorize_with_record():
    @app.route('/helloworld')
    def hello_world():
        g.user = {'user': {'id':1, 'role': 'admin'}}
        post = Post()
        is_authorized = authorize(post)
        if is_authorized:
            return 'Success', 200
        else:
            return 'Unauthorized', 403
    resp = client.get('/helloworld')
    eq_(resp.status_code, 200)
