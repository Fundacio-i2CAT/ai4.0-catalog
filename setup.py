# -*- coding: utf-8 -*-
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

from setuptools import setup, find_packages


setup(name='anella',
    version='0.0.1',
    description='Anella-Catalog',
    long_description='',
    classifiers=[
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    author='',
    author_email='oscar.rambla@i2cat.net',
    url='',
    keywords='web mongo',
    license='Apache License, http://www.apache.org/licenses/LICENSE-2.0',
    platforms=['Linux', 'MacOS X'],
    install_requires=[
        'simplejson >= 3',
        "pymongo >= 2.0",
        "PyYAML >= 3.09",
        "python-dateutil >= 1.4.1",
        "requests",
        "jsonschema",
        "mongoengine"
    ],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    zip_safe=False,
    test_suite="anella",
    tests_require=[
        'pytidylib',
        'nose'
        'mock',
        'coverage',
        'pep8',
        'pylint'
 
    ],
    package_data={
        'anella': [
            'i18n/*/LC_MESSAGES/*.mo', 'templates/*/*', 'public/*/*']
    },
    message_extractors={
        'anella': [
            ('**.py', 'python', None),
            ('public/**', 'ignore', None)]
    },
    entry_points="""
    """
)
