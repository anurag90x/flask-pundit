# Flask-Pundit [![Build Status](https://travis-ci.org/anurag90x/flask-pundit.svg?branch=master)](https://travis-ci.org/anurag90x/flask-pundit)  
A simple flask extension to organize resource authorization and scoping. This extension is heavily inspired by the ruby Pundit library.

## Installation
` pip install flask-pundit `

## Usage
Just like with the Pundit library, the idea is to offer a way for organizing authorization code. As such, authorization code should exist in Policy
classes and there should be a single Policy class per model class. For example, if you're using [Flask-RESTful](https://github.com/flask-restful/flask-restful),
your project structure might be something like
```
project
|-- resources
|-- models
|    |-- post.py
|    |-- comment.py
|-- policies
|    |-- post.py
|    |-- comment.py
|-- app.py
```
### Initialization

You can initialize the extension in one of 2 ways - 

1. `pundit = FlaskPundit(app)` where app is the application object.
2. `pundit.init_app(app)` after constructing the FlaskPundit object without an app object. 

When initializing the extension, you can provide an optional `policies_path` parameter which tells Flask-Pundit where to find your policy classes. If no value is specified this defaults to `policies`.

Now onto how to actually use the extension.

### Authorization
Flask-Pundit like Pundit offers two methods for use in resources (or if you like, controllers). The first is the `authorize` method. This is how you would use
the method if you're writing a simple single module app.

```python
app = Flask('blog_series')
pundit = FlaskPundit(app)

@app.route('/blogs/<id>')
def read_blog(blog_id):
        blog = Blogs.get_by_id(blog_id)
        if pundit.authorize(blog):
                return blog
        return ForbiddenError, 403
```

The authorize method takes 3 parameters:

1. A record - This can be either an object or class and corresponds to a 'model' that you're doing the authorization on.

2. An action - This corresponds to the policy method that you want to invoke for doing the authorization. If no value is provided it
defaults to `request.method.lowercase()`. Thus in the previous snippet the `get` method of a `BlogPolicy` object would be invoked.

3. A user - This is akin to the currently 'logged in' user. If no user object is provided, flask-pundit tries to pick either `flask.g.user` or 
`flask.g.current_user`, whichever is available.


