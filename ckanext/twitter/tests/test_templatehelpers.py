#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-twitter
# Created by the Natural History Museum in London, UK

import mock
import nose
from ckantest.factories import DataConstants
from ckantest.models import TestBase

from ckanext.twitter.lib.helpers import TwitterJSHelpers, twitter_pkg_suitable


class TestGetConfigVariables(TestBase):
    plugins = [u'twitter', u'datastore']
    persist = {
        u'ckanext.twitter.debug': True
        }

    @classmethod
    def setup_class(cls):
        super(TestGetConfigVariables, cls).setup_class()
        cls.js_helpers = TwitterJSHelpers()

    def tearDown(self):
        self.config.soft_reset()

    def run(self, result=None):
        with mock.patch('ckanext.twitter.plugin.session', self._session):
            super(TestGetConfigVariables, self).run(result)

    @property
    def _public_records(self):
        if self.data_factory().packages.get('public_records', None) is None:
            pkg_dict = self.data_factory().package(name='public_records')
            self.data_factory().resource(package_id=pkg_dict[u'id'],
                                         records=DataConstants.records)
        return self.data_factory().packages['public_records']

    def test_gets_context(self):
        assert isinstance(self.js_helpers.context, dict)

    def test_returns_false_if_not_in_session(self):
        self._session.clear()
        pkg_dict = self.data_factory().package()
        with mock.patch('ckanext.twitter.lib.helpers.session', self._session):
            nose.tools.assert_equal(self.js_helpers.tweet_ready(pkg_dict[u'id']),
                                    False)

    def test_returns_true_if_is_in_session(self):
        pkg_dict = self.data_factory().package()
        self._session.setdefault(u'twitter_is_suitable',
                                 pkg_dict[u'id'])
        self._session.save()
        with mock.patch('ckanext.twitter.lib.helpers.session', self._session):
            nose.tools.assert_equal(self.js_helpers.tweet_ready(pkg_dict[u'id']), True)

    def test_gets_tweet(self):
        self.config.remove(u'ckanext.twitter.new')
        pkg_dict = self.data_factory().package()
        nose.tools.assert_equal(self.js_helpers.get_tweet(pkg_dict[u'id']),
                                u'New dataset: "{0}" by {1} (0 resource).'.format(
                                    DataConstants.title_short,
                                    DataConstants.authors_short_first))

    def test_not_suitable_if_does_not_exist(self):
        is_suitable = twitter_pkg_suitable(self.data_factory().context, u'not-a-real-id')
        nose.tools.assert_equal(is_suitable, False)

    def test_not_suitable_if_not_active(self):
        # not active
        self.data_factory().deactivate_package(self._public_records[u'id'])
        assert self._public_records[u'state'] != u'active'

        # not draft
        assert self._public_records[u'state'] != u'draft'

        # is suitable
        is_suitable = twitter_pkg_suitable(self.data_factory().context,
                                           self._public_records[u'id'])
        nose.tools.assert_equal(is_suitable, False)

        # undo
        self.data_factory().refresh()

    def test_not_suitable_if_no_resources(self):
        # active
        nose.tools.assert_equal(self._public_records[u'state'], u'active')

        # has no resources
        self.data_factory().remove_resources(self._public_records[u'name'])
        nose.tools.assert_equal(len(self._public_records.get(u'resources', [])), 0)

        # is suitable
        is_suitable = twitter_pkg_suitable(self.data_factory().context,
                                           self._public_records[u'id'])
        nose.tools.assert_equal(is_suitable, False)

        # undo
        self.data_factory().refresh()

    def test_not_suitable_if_no_active_resources(self):
        pkg_dict = self.data_factory().deactivate_resources(self._public_records[u'name'])
        # exists
        assert pkg_dict is not None

        # active
        nose.tools.assert_equal(pkg_dict[u'state'], u'active')

        # has resources
        assert len(pkg_dict[u'resources']) > 0

        # resources are not active
        active_resources = [r[u'state'] == u'active' for r in
                            pkg_dict[u'resources']]
        nose.tools.assert_equal(any(active_resources), False,
                                u'{0}/{1} resources still active'.format(sum(active_resources),
                                                                         len(active_resources)))

        # is suitable
        is_suitable = twitter_pkg_suitable(self.data_factory().context,
                                           None, pkg_dict)
        nose.tools.assert_equal(is_suitable, False)

    def test_not_suitable_if_private(self):
        pkg_dict = self.data_factory().package(name=u'private_records', private=True)
        self.data_factory().resource(package_id=pkg_dict[u'id'],
                                     records=DataConstants.records)

        # active
        nose.tools.assert_equal(self.data_factory().packages[u'private_records'][u'state'],
                                u'active')

        # has resources
        assert len(self.data_factory().packages[u'private_records'][u'resources']) > 0

        # resources are active
        active_resources = [r[u'state'] == u'active' for r in
                            self.data_factory().packages[u'private_records'][u'resources']]
        nose.tools.assert_equal(any(active_resources), True)

        # is private
        nose.tools.assert_equal(
            self.data_factory().packages[u'private_records'].get(u'private', False), True)

        # is suitable
        is_suitable = twitter_pkg_suitable(self.data_factory().context,
                                           self.data_factory().packages[u'private_records'][u'id'])
        nose.tools.assert_equal(is_suitable, False)

    def test_otherwise_suitable(self):
        # active
        nose.tools.assert_equal(self._public_records[u'state'], u'active')

        # has resources
        assert len(self._public_records[u'resources']) > 0

        # resources are active
        active_resources = [r[u'state'] == u'active' for r in
                            self._public_records[u'resources']]
        nose.tools.assert_equal(any(active_resources), True)

        # not private
        nose.tools.assert_equal(self._public_records.get(u'private', False), False)

        # is suitable
        is_suitable = twitter_pkg_suitable(self.data_factory().context,
                                           self._public_records[u'id'])
        nose.tools.assert_equal(is_suitable, True)
