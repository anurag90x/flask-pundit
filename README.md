# Flask-Pundit [![Build Status](https://travis-ci.org/anurag90x/flask-pundit.svg?branch=master)](https://travis-ci.org/anurag90x/flask-pundit)  
A simple flask extension to organize resource authorization and scoping. This extension is heavily inspired by the ruby Pundit library.

## Installation
` pip install flask-pundit `

## Initialization

You can initialize the extension in one of 2 ways - 

1. `pundit = FlaskPundit(app)` where app is the application object.
2. `pundit.init_app(app)` after constructing the FlaskPundit object without an app object. 

When initializing the extension, you can provide an optional `policies_path` parameter which tells Flask-Pundit where to find your policy classes. If no value is specified this defaults to `policies`.

What is this `policies_path` exactly?

Flask-Pundit expects you to have 1 policy per model class. To find the Policy for a particular model it needs to know where to look. That is the `policies_path`. 

## Policies

A policy class defines the 'rules' used to authorize a model. You can write your own policy class as follows:

```python
class PostPolicy():
        def __init__(self, user, post):
                self.user = user
                self.post = post
        
        def get(self):
                return self.user == 'admin' and self.post.id == 1
```
The user object is the currently 'logged' in user and the post object is the model instance you want to authorize.
The `get` method is an authorization 'action' handler that you might want to execute when a user is trying to read a post.

You could alternatively define your own `BasePolicy` class and extend it in a similar fashion or use the `ApplicationPolicy` class provided by the extension in which case the code would be:

```python
from flask_pundit.application_policy import ApplicationPolicy

class PostPolicy(ApplicationPolicy):
        def get(self):
                return self.user == 'admin' and self.record.id == 1
```
Note that now we're using `record` inside the method. By inheriting from `ApplicationPolicy` all instance methods now use `record` to represent the model instance being authorized.

To authorize a post object inside a resource (or a blueprint or just a app.route decorated function) you would call `self.pundit.authorize(post)`. This will cause flask-pundit to look for the `PostPolicy` class at `policies/post`. If you want a different root to be searched, you can specify the ` policies_path` when initializing the extension.

This example shows how to use the authorize method in a single module app.

```python
app = Flask('blog_series')
pundit = FlaskPundit(app)

@app.route('/blogs/<id>')
def read_blog_post(id):
        blog = Post.get_by_id(id)
        if pundit.authorize(post):
                return blog
        return ForbiddenError, 403
```
The authorize method takes 3 parameters:

1. A record - This can be either an object or class and corresponds to a 'model' that you're doing the authorization on.

2. An action - This corresponds to the policy method that you want to invoke for doing the authorization. If no value is provided it
defaults to `request.method.lowercase()`. Thus in the previous snippet the `get` method of a `BlogPolicy` object would be invoked.

3. A user - This is akin to the currently 'logged in' user. If no user object is provided, flask-pundit tries to pick either `flask.g.user` or 
`flask.g.current_user`, whichever is available.

Thus in the above set of examples, invoking `authorize` executes the `get` method in the `PostPolicy` class at `policies/post` with the record being the `post` object filtered by id.

## Scopes

The `authorize` method acts more as a true/false guard. On the other hand the `policy_scope` method returns a 'scoped' version of a model. For example, if you have a page with all posts, you might want to let an admin see all of them but restrict the ones staff users see. This is where you'd want to use `policy_scope` instead of `authorize`.

To do so, you need to first have a `Scope` class. Scopes are classes that help you return 'scoped' versions of models. You can define a scope as:

```python
from flask_pundit.application_policy import ApplicationPolicy

class PostPolicy(ApplicationPolicy):
        def get(self):
                return self.user == 'admin' and self.record.id == 1
        
        class Scope():
                def __init__(self, user, scope):
                        self.user = user
                        self.scope = scope

                def resolve(self):
                        if self.user == 'admin':
                                return scope.all()
                        return scope.filter_by(author='staff')
```
The `Scope` class for a model should always be an inner class of the corresponding Policy class. The constructor takes 2 arguments - the user (exactly like in the Policy class) and a `scope` which is the model you want to return a subset of.

Instead of writing the constructor every time you need a scope you could also just inherit from `ApplicationPolicy.Scope`.

When you call the `policy_scope(model)` with a model class (it doesn't make sense to pass an object here), the `resolve` method gets called.

``` python
from app import pundit

@app.route('/posts)
def index():
        all_posts = pundit.policy_scope(Post)
        return all_posts
```
The examples here show how to return all posts for an admin and only staff posts for a staff user.

The `policy_scope` method takes 2 arguments:

1. A model - This is the class that is to be 'scoped'.

2. A user object - This is just like the user object in the authorize case.

## Verification

Flask-Pundit has 2 decorators you can use to verify `authorize`/ `policy_scope` has been called. They are `verify_authorized` and `verify_policy_scoped`.

In a single module app you would use `verify_authorized` as:

``` python
from flask_pundit import verify_authorized
from app import app, pundit

@app.route('/posts/<id>')
@verify_authorized
def read_blog_post(id):
        blog_post = Post.get_by_id(id)
        if pundit.authorize(blog_post):
                return blog_post
        return ForbiddenError, 403
```
If you remove the call to `authorize` the decorator will throw a `RuntimeError` as it expects a call but found none.

The `verify_policy_scoped` decorator would be used in the exact same way. Using these 2 would prove more useful if you're using something like [Flask-Restful](https://github.com/flask-restful/flask-restful) where you could specify these as `method_decorators` in your resource, if you wanted all the methods to be verified.

If you prefer not using decorators you could use `pundit._verify_authorized` and `pundit._verify_policy_scoped` directly inside your methods. Calling them directly will return `True` or `False`.

## Custom Policy class

You could override the policy class lookup behaviour by adding a `__policy_class__` property on your models. This should reference the class that you want to be used against this model. For example,

```python
from policies.commenting import CommentingPolicy

class Comment:
        __policy_class__ = CommentingPolicy
```
Now when doing either `authorize` or `policy_scope` against an instance of `Comment` or the class itself, `CommentingPolicy` will be used.

## License

Licensed under MIT license
