#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-twitter
# Created by the Natural History Museum in London, UK

from setuptools import find_packages, setup

__version__ = '2.0.0'

with open('README.md', 'r') as f:
    __long_description__ = f.read()

setup(
    name='ckanext-twitter',
    version=__version__,
    description='A CKAN extension that enables users to post a tweet every time a dataset is '
                'created or updated.',
    long_description=__long_description__,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    keywords='CKAN data twitter',
    author='Natural History Museum',
    author_email='data@nhm.ac.uk',
    url='https://github.com/NaturalHistoryMuseum/ckanext-twitter',
    license='GNU GPLv3',
    packages=find_packages(exclude=['tests']),
    namespace_packages=['ckanext', 'ckanext.twitter'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'oauth2==1.9.0.post1',
    ],
    entry_points= \
        '''
        [ckan.plugins]
            twitter=ckanext.twitter.plugin:TwitterPlugin

        ''',
)
