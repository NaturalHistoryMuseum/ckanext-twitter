#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-twitter
# Created by the Natural History Museum in London, UK

import mock
import nose
from ckantest.factories import DataConstants
from ckantest.models import TestBase

from ckanext.twitter.lib import (cache_helpers, parsers as twitter_parsers,
                                 twitter_api)


class TestTweetGeneration(TestBase):
    plugins = [u'twitter', u'datastore']
    persist = {
        u'ckanext.twitter.debug': True
        }

    @classmethod
    def setup_class(cls):
        super(TestTweetGeneration, cls).setup_class()
        cache_helpers.reset_cache()

    def tearDown(self):
        self.config.soft_reset()

    def run(self, result=None):
        with mock.patch('ckanext.twitter.plugin.session', self._session):
            super(TestTweetGeneration, self).run(result)

    @property
    def _public_records(self):
        if self.data_factory().packages.get('public_records', None) is None:
            pkg_dict = self.data_factory().package(name='public_records')
            self.data_factory().resource(package_id=pkg_dict[u'id'],
                                                records=DataConstants.records)
        return self.data_factory().packages['public_records']

    def test_generates_tweet_if_public(self):
        tweet_text = twitter_parsers.generate_tweet(self.data_factory().context,
                                                    self._public_records[u'id'],
                                                    is_new=True)
        assert tweet_text is not None

    def test_does_not_generate_tweet_if_private(self):
        pkg_dict = self.data_factory().package(private=True)
        tweet_text = twitter_parsers.generate_tweet(self.data_factory().context,
                                                    pkg_dict[u'id'],
                                                    is_new=True)
        nose.tools.assert_equal(tweet_text, None)

    def test_generates_correct_tweet_for_new(self):
        # delete the config value so it's using the default
        self.config.remove(u'ckanext.twitter.new')
        tweet_text = twitter_parsers.generate_tweet(self.data_factory().context,
                                                    self._public_records[u'id'],
                                                    is_new=True)
        correct_tweet_text = u'New dataset: "{0}" by {1} (5 records).'.format(
            DataConstants.title_short, DataConstants.authors_short_first)
        nose.tools.assert_equal(tweet_text, correct_tweet_text)

    def test_generates_correct_tweet_for_updated(self):
        # delete the config value so it's using the default
        self.config.remove(u'ckanext.twitter.update')
        tweet_text = twitter_parsers.generate_tweet(self.data_factory().context,
                                                    self._public_records[u'id'],
                                                    is_new=False)
        correct_tweet_text = u'Updated dataset: "{0}" by {1} (5 records).'.format(
            DataConstants.title_short, DataConstants.authors_short_first)
        nose.tools.assert_equal(tweet_text, correct_tweet_text)

    def test_does_not_tweet_when_debug(self):
        assert u'ckanext.twitter.debug' in self.config.current
        assert self.config.current.get(u'ckanext.twitter.debug', False)
        tweeted, reason = twitter_api.post_tweet(u'This is a test tweet.',
                                                 self._public_records[u'id'])
        nose.tools.assert_equal(tweeted, False)
        nose.tools.assert_equal(reason, u'debug')

    def test_shortens_author(self):
        # delete the config value so it's using the default
        self.config.remove(u'ckanext.twitter.new')
        pkg_dict = self.data_factory().package(author=DataConstants.authors_long)
        tweet_text = twitter_parsers.generate_tweet(self.data_factory().context,
                                                    pkg_dict[u'id'],
                                                    is_new=True)
        correct_tweet_text = u'New dataset: "{0}" by {1} et al.' \
                             u' (0 resource).'.format(DataConstants.title_short,
                                                      DataConstants.authors_long_first)
        nose.tools.assert_equal(tweet_text, correct_tweet_text)

    def test_shortens_title(self):
        # delete the config value so it's using the default
        self.config.remove(u'ckanext.twitter.new')
        pkg_dict = self.data_factory().package(title=DataConstants.title_long)
        tweet_text = twitter_parsers.generate_tweet(self.data_factory().context,
                                                    pkg_dict[u'id'],
                                                    is_new=True)
        correct_tweet_text = u'New dataset: "{0}[...]" by {1} (0 resource).'.format(
            DataConstants.title_long[:41], DataConstants.authors_short_first)
        nose.tools.assert_equal(tweet_text, correct_tweet_text)

    def test_does_not_exceed_140_chars(self):
        # delete the config value so it's using the default
        self.config.remove(u'ckanext.twitter.new')
        pkg_dict = self.data_factory().package(author=DataConstants.authors_long,
                                               title=DataConstants.title_long)
        force_truncate = twitter_parsers.generate_tweet(self.data_factory().context,
                                                        pkg_dict[u'id'],
                                                        is_new=True)
        no_force = twitter_parsers.generate_tweet(self.data_factory().context,
                                                  pkg_dict[u'id'],
                                                  is_new=True,
                                                  force_truncate=False)
        assert len(force_truncate) <= 140
        assert len(no_force) <= 140

    def test_does_not_tweet_when_recently_tweeted(self):
        # make sure it can't send an actual tweet by removing the credentials
        cache_helpers.reset_cache()
        self.config.remove(u'ckanext.twitter.key', u'ckanext.twitter.secret',
                            u'ckanext.twitter.token_key',
                            u'ckanext.twitter.token_secret')
        # turn off debug so it skips that check
        self.config.update({
            u'debug': False,
            u'ckanext.twitter.debug': False
            })
        # emulate successful tweet by manually inserting into the cache
        cache_helpers.cache(self._public_records[u'id'])
        # try to tweet
        tweeted, reason = twitter_api.post_tweet(u'This is a test tweet.',
                                                 self._public_records[u'id'])
        nose.tools.assert_equal(tweeted, False)
        nose.tools.assert_equal(reason, u'insufficient rest period')

    def test_does_tweet_when_new(self):
        # make sure it can't send an actual tweet by removing the credentials
        cache_helpers.reset_cache()
        self.config.remove(u'ckanext.twitter.consumer_key', u'ckanext.twitter.consumer_secret',
                            u'ckanext.twitter.token_key',
                            u'ckanext.twitter.token_secret')
        # turn off debug so it skips that check
        self.config.update({
            u'debug': False,
            u'ckanext.twitter.debug': False
            })
        # create new package to see if it's sending tweets during creation
        pkg_dict = self.data_factory().package()
        # try to tweet
        tweeted, reason = twitter_api.post_tweet(u'This is a test tweet.',
                                                 pkg_dict[u'id'])
        config_keys = [k for k in self.config.current.keys() if k.startswith('ckanext.twitter')]
        nose.tools.assert_equal(tweeted, False,
                                'Tweet WAS posted! These config options are still present:\n {'
                                '0}'.format(
                                    '\n'.join(config_keys)))
        nose.tools.assert_equal(reason, u'not authenticated')
