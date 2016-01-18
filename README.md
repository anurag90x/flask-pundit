# Flask-Pundit [![Build Status](https://travis-ci.org/anurag90x/flask-pundit.svg?branch=master)](https://travis-ci.org/anurag90x/flask-pundit)  
A simple flask extension to organize resource authorization and scoping. This extensions is heavily inspired by the ruby Pundit library.

## Installation
` pip install flask-pundit `

## Usage
Just like the Pundit library the idea is to offer a way for organizing authorization code. As such, authorization code should exist in Policy
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

