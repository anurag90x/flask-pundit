from flask_pundit.import_helpers import import_module
from nose.tools import assert_raises, eq_

def test_existing_module_path():
    module = import_module('tests.policies.post')
    eq_(module.__name__, 'tests.policies.post')

def test_non_existing_module_path():
    assert_raises(ImportError, import_module, 'tests.random_mod')
