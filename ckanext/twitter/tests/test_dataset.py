#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-twitter
# Created by the Natural History Museum in London, UK

import mock
import nose
from ckantest.factories import DataConstants
from ckantest.models import TestBase

from ckanext.twitter.lib import (parsers as twitter_parsers)


class TestDatasetMetadata(TestBase):
    plugins = [u'twitter', u'datastore']
    persist = {
        u'ckanext.twitter.debug': True
        }

    def run(self, result=None):
        with mock.patch('ckanext.twitter.plugin.session', self._session):
            super(TestDatasetMetadata, self).run(result)

    @property
    def _public_records(self):
        if self.data_factory().packages.get('public_records', None) is None:
            pkg_dict = self.data_factory().package(name='public_records')
            return self.data_factory().resource(package_id=pkg_dict[u'id'],
                                                records=DataConstants.records)
        return self.data_factory().packages['public_records']

    def test_gets_dataset_author(self):
        nose.tools.assert_equal(self._public_records[u'author'], DataConstants.authors_short,
                                u'Author is actually: {0}'.format(
                                    self._public_records.get(u'author', u'no author set')))

    def test_gets_dataset_title(self):
        nose.tools.assert_equal(self._public_records[u'title'], DataConstants.title_short,
                                u'Title is actually: {0}'.format(
                                    self._public_records.get(u'title', u'no title set')))

    def test_gets_dataset_number_of_records_if_has_records(self):
        n_records = twitter_parsers.get_number_records(self.data_factory().context,
                                                       self._public_records[u'id'])
        nose.tools.assert_equal(n_records, 5,
                                u'Calculated number of records: {0}\nActual number: 5'.format(
                                    n_records))

    def test_gets_dataset_number_of_records_if_no_records(self):
        pkg_dict = self.data_factory().package()
        n_records = twitter_parsers.get_number_records(self.data_factory().context,
                                                       pkg_dict[u'id'])
        nose.tools.assert_equal(n_records, 0,
                                u'Calculated number of records: {0}\nActual number: 0'.format(
                                    n_records))

    def test_gets_is_private(self):
        if self._public_records.get(u'private', None) is None:
            access = u'unknown'
        elif self._public_records.get(u'private', None):
            access = u'private'
        else:
            access = u'public'
        nose.tools.assert_equal(self._public_records[u'private'], False,
                                u'Package is actually: {0}'.format(access))
