from nose.tools import eq_
from flask_pundit.helpers import dasherized_name


def test_dasherized_name__simple():
    eq_('post', dasherized_name('post'))


def test_dasherized_name__simple_uppercase():
    eq_(dasherized_name('Post'), 'post')


def test_dasherized_name__simple_camelcase():
    eq_(dasherized_name('ProjectPost'), 'project_post')


def test_dasherized_name__complex_camelcase():
    eq_(dasherized_name('PRTestingClass'), 'prtesting_class')
