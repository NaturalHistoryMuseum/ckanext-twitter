#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-twitter
# Created by the Natural History Museum in London, UK

import nose
from ckantest.models import TestBase

import ckanext.twitter.lib.config_helpers as config_helpers
from ckan.plugins import toolkit


class TestGetConfigVariables(TestBase):
    plugins = [u'twitter']
    persist = {
        u'ckanext.twitter.debug': True
        }

    def teardown(self):
        self.config.reset()

    def _set_config_value(self, key, has_var, test_value=None):
        if has_var:
            self.config.update({
                u'ckanext.twitter.' + key: test_value
                })
        else:
            self.config.remove([u'ckanext.twitter.' + key])

    def test_gets_debug_value_when_present(self):
        test_value = False
        self._set_config_value(u'debug', True, test_value)
        config_value = toolkit.config.get(u'ckanext.twitter.debug')
        nose.tools.assert_equal(test_value, config_value)

    def test_gets_debug_default_when_absent(self):
        default_value = True
        self._set_config_value(u'debug', False)
        config_value = toolkit.config.get(u'ckanext.twitter.debug',
                                          default_value)
        nose.tools.assert_equal(default_value, config_value)

    def test_gets_hours_between_tweets_value_when_present(self):
        test_value = 2
        self._set_config_value(u'hours_between_tweets', True, test_value)
        config_value = config_helpers \
            .twitter_hours_between_tweets()
        nose.tools.assert_equal(test_value, config_value)

    def test_gets_hours_between_tweets_default_when_absent(self):
        default_value = 24
        self._set_config_value(u'hours_between_tweets', False)
        config_value = \
            config_helpers.twitter_hours_between_tweets()
        nose.tools.assert_equal(default_value, config_value)

    def test_gets_credentials_when_present(self):
        test_key = u'test-key-value'
        test_secret = u'test-secret-value'
        test_tk = u'test-token-key'
        test_ts = u'test-token-secret'
        self._set_config_value(u'consumer_key', True, test_key)
        self._set_config_value(u'consumer_secret', True, test_secret)
        self._set_config_value(u'token_key', True, test_tk)
        self._set_config_value(u'token_secret', True, test_ts)
        ck, cs, tk, ts = \
            config_helpers.twitter_get_credentials()
        nose.tools.assert_equal(test_key, ck)
        nose.tools.assert_equal(test_secret, cs)
        nose.tools.assert_equal(test_tk, tk)
        nose.tools.assert_equal(test_ts, ts)

    def test_gets_no_credentials_when_absent(self):
        self._set_config_value(u'consumer_key', False)
        self._set_config_value(u'consumer_secret', False)
        self._set_config_value(u'token_key', False)
        self._set_config_value(u'token_secret', False)
        ck, cs, tk, ts = config_helpers.twitter_get_credentials()
        nose.tools.assert_equal(u'no-consumer-key-set', ck)
        nose.tools.assert_equal(u'no-consumer-secret-set', cs)
        nose.tools.assert_equal(u'no-token-key-set', tk)
        nose.tools.assert_equal(u'no-token-secret-set', ts)

    def test_gets_disable_edit_value_when_present(self):
        test_value = True
        self._set_config_value(u'disable_edit', True, test_value)
        config_value = config_helpers.twitter_disable_edit()
        nose.tools.assert_equal(test_value, config_value)

    def test_gets_disable_edit_default_when_absent(self):
        default_value = False
        self._set_config_value(u'disable_edit', False)
        config_value = \
            config_helpers.twitter_disable_edit()
        nose.tools.assert_equal(default_value, config_value)
