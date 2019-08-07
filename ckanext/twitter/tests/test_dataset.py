#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-twitter
# Created by the Natural History Museum in London, UK

import ckantest.helpers
import mock
import nose
from ckantest.models import TestBase

from ckanext.twitter.lib import (parsers as twitter_parsers)

eq_ = nose.tools.eq_


class TestDatasetMetadata(TestBase):
    plugins = [u'twitter', u'datastore']
    persist = {
        u'ckanext.twitter.debug': True
        }

    def run(self, result=None):
        with mock.patch('ckanext.twitter.plugin.session', self._session):
            super(TestDatasetMetadata, self).run(result)

    def test_gets_dataset_author(self):
        pkg_dict = self.data_factory().public_records
        eq_(pkg_dict[u'author'], u'Test Author',
            u'Author is actually: {0}'.format(
                pkg_dict.get(u'author', u'no author set')))

    def test_gets_dataset_title(self):
        pkg_dict = self.data_factory().public_records
        eq_(pkg_dict[u'title'], u'A test package',
            u'Title is actually: {0}'.format(
                pkg_dict.get(u'title', u'no title set')))

    def test_gets_dataset_number_of_records_if_has_records(self):
        pkg_dict = self.data_factory().public_records
        n_records = twitter_parsers.get_number_records(self.data_factory().context,
                                                       pkg_dict[u'id'])
        eq_(n_records, 5,
            u'Calculated number of records: {0}\nActual number: 5'.format(
                n_records))

    def test_gets_dataset_number_of_records_if_no_records(self):
        pkg_dict = self.data_factory().public_no_records
        n_records = twitter_parsers.get_number_records(self.data_factory().context,
                                                       pkg_dict[u'id'])
        eq_(n_records, 0,
            u'Calculated number of records: {0}\nActual number: 0'.format(
                n_records))

    def test_gets_is_private(self):
        pkg_dict = self.data_factory().public_records
        if pkg_dict.get(u'private', None) is None:
            access = u'unknown'
        elif pkg_dict.get(u'private', None):
            access = u'private'
        else:
            access = u'public'
        eq_(pkg_dict[u'private'], False,
            u'Package is actually: {0}'.format(access))
