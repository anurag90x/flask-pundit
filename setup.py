from setuptools import setup, find_packages
import sys

PY26 = sys.version_info[:2] == (2, 6,)

requirements = [
    'Flask>=0.8',
]

setup(
    name='Flask-Pundit',
    version='0.0.1',
    license='BSD',
    url='https://www.github.com/flask-pundit/flask-pundit/',
    author='Anurag Chaudhury',
    author_email='anuragchaudhury@gmail.com',
    description='Simple library to manage permissions and scopes',
    packages=find_packages(exclude=['tests']),
    classifiers=[
        'Framework :: Flask',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'License :: OSI Approved :: BSD License',
    ],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    test_suite = 'nose.collector',
    install_requires=requirements,
    tests_require=['mock>=0.8']
)
