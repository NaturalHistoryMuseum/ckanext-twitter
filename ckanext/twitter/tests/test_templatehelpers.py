#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-twitter
# Created by the Natural History Museum in London, UK

import ckantest.factories
import ckantest.helpers
import nose

from ckan import plugins
from ckan.common import session
from ckan.tests import helpers
from ckanext.twitter.lib.helpers import TwitterJSHelpers, twitter_pkg_suitable

eq_ = nose.tools.eq_


class TestGetConfigVariables(helpers.FunctionalTestBase):
    @classmethod
    def setup_class(cls):
        super(TestGetConfigVariables, cls).setup_class()
        ckantest.helpers.plugins.load_datastore()
        plugins.load(u'twitter')
        cls.config = ckantest.helpers.Configurer()
        cls.df = ckantest.factories.DataFactory()
        cls.js_helpers = TwitterJSHelpers()

    def teardown(self):
        self.config.reset()

    @classmethod
    def teardown_class(cls):
        cls.config.reset()
        cls.df.destroy()
        ckantest.helpers.plugins.unload_datastore()
        plugins.unload(u'twitter')

    def test_gets_context(self):
        assert isinstance(self.js_helpers.context, dict)

    def test_returns_false_if_not_in_session(self):
        session.clear()
        eq_(self.js_helpers.tweet_ready(self.df.public_no_records[u'id']),
            False)

    def test_returns_true_if_is_in_session(self):
        session.setdefault(u'twitter_is_suitable',
                           self.df.public_no_records[u'id'])
        session.save()
        eq_(self.js_helpers.tweet_ready(self.df.public_no_records[u'id']), True)

    def test_gets_tweet(self):
        self.config.remove([u'ckanext.twitter.new'])
        eq_(self.js_helpers.get_tweet(self.df.public_no_records[u'id']),
            u'New dataset: "A test package" by Author (1 resource).')

    def test_not_suitable_if_does_not_exist(self):
        is_suitable = twitter_pkg_suitable(self.df.context, u'not-a-real-id')
        eq_(is_suitable, False)

    def test_not_suitable_if_not_active(self):
        # exists
        self.df.reload_pkg_dicts()
        assert self.df.public_records is not None

        # not active
        self.df.deactivate_package(self.df.public_records[u'id'])
        assert self.df.public_records[u'state'] != u'active'

        # not draft
        assert self.df.public_records[u'state'] != u'draft'

        # is suitable
        is_suitable = twitter_pkg_suitable(self.df.context,
                                           self.df.public_records[u'id'])
        eq_(is_suitable, False)

        # undo the deactivation
        self.df.activate_package(self.df.public_records[u'id'])

    def test_not_suitable_if_no_resources(self):
        # exists
        self.df.reload_pkg_dicts()
        assert self.df.public_records is not None

        # active
        eq_(self.df.public_records[u'state'], u'active')

        # has no resources
        self.df.remove_public_resources()
        eq_(len(self.df.public_records.get(u'resources', [])), 0)

        # is suitable
        is_suitable = twitter_pkg_suitable(self.df.context,
                                           self.df.public_records[u'id'])
        eq_(is_suitable, False)

        # undo
        self.df.refresh()

    def test_not_suitable_if_no_active_resources(self):
        pkg_dict = self.df.deactivate_public_resources()
        # exists
        assert pkg_dict is not None

        # active
        eq_(pkg_dict[u'state'], u'active')

        # has resources
        assert len(pkg_dict[u'resources']) > 0

        # resources are not active
        active_resources = [r[u'state'] == u'active' for r in
                            pkg_dict[u'resources']]
        eq_(any(active_resources), False,
            u'{0}/{1} resources still active'.format(sum(active_resources),
                                                     len(active_resources)))

        # is suitable
        is_suitable = twitter_pkg_suitable(self.df.context,
                                           None, pkg_dict)
        eq_(is_suitable, False)

    def test_not_suitable_if_private(self):
        # exists
        self.df.reload_pkg_dicts()
        assert self.df.private_records is not None

        # active
        eq_(self.df.private_records[u'state'], u'active')

        # has resources
        assert len(self.df.private_records[u'resources']) > 0

        # resources are active
        active_resources = [r[u'state'] == u'active' for r in
                            self.df.private_records[u'resources']]
        eq_(any(active_resources), True)

        # is private
        eq_(self.df.private_records.get(u'private', False), True)

        # is suitable
        is_suitable = twitter_pkg_suitable(self.df.context,
                                           self.df.private_records[u'id'])
        eq_(is_suitable, False)

    def test_otherwise_suitable(self):
        # exists
        self.df.reload_pkg_dicts()
        assert self.df.public_records is not None

        # active
        eq_(self.df.public_records[u'state'], u'active')

        # has resources
        assert len(self.df.public_records[u'resources']) > 0

        # resources are active
        active_resources = [r[u'state'] == u'active' for r in
                            self.df.public_records[u'resources']]
        eq_(any(active_resources), True)

        # not private
        eq_(self.df.public_records.get(u'private', False), False)

        # is suitable
        is_suitable = twitter_pkg_suitable(self.df.context,
                                           self.df.public_records[u'id'])
        eq_(is_suitable, True)
