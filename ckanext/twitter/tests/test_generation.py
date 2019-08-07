#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-twitter
# Created by the Natural History Museum in London, UK

import nose
import mock
from ckantest.models import TestBase

from ckanext.twitter.lib import (cache_helpers, parsers as twitter_parsers,
                                 twitter_api)

eq_ = nose.tools.eq_


class TestTweetGeneration(TestBase):
    plugins = [u'twitter', u'datastore']
    persist = {
        u'ckanext.twitter.debug': True
        }

    @classmethod
    def setup_class(cls):
        super(TestTweetGeneration, cls).setup_class()
        cache_helpers.reset_cache()

    def teardown(self):
        self.config.reset()

    def run(self, result=None):
        with mock.patch('ckanext.twitter.plugin.session', self._session):
            super(TestTweetGeneration, self).run(result)

    def test_generates_tweet_if_public(self):
        tweet_text = twitter_parsers.generate_tweet(self.data_factory().context,
                                                    self.data_factory().public_records[
                                                        u'id'],
                                                    is_new=True)
        assert tweet_text is not None

    def test_does_not_generate_tweet_if_private(self):
        tweet_text = twitter_parsers.generate_tweet(self.data_factory().context,
                                                    self.data_factory().private_records[
                                                        u'id'],
                                                    is_new=True)
        eq_(tweet_text, None)

    def test_generates_correct_tweet_for_new(self):
        # delete the config value so it's using the default
        self.config.remove([u'ckanext.twitter.new'])
        tweet_text = twitter_parsers.generate_tweet(self.data_factory().context,
                                                    self.data_factory().public_records[
                                                        u'id'],
                                                    is_new=True)
        correct_tweet_text = u'New dataset: "A test package" by Author (' \
                             u'5 records).'
        eq_(tweet_text, correct_tweet_text)

    def test_generates_correct_tweet_for_updated(self):
        # delete the config value so it's using the default
        self.config.remove([u'ckanext.twitter.update'])
        tweet_text = twitter_parsers.generate_tweet(self.data_factory().context,
                                                    self.data_factory().public_records[
                                                        u'id'],
                                                    is_new=False)
        correct_tweet_text = u'Updated dataset: "A test package" by Author' \
                             u' (5 records).'
        eq_(tweet_text, correct_tweet_text)

    def test_does_not_tweet_when_debug(self):
        self.config.update({
            u'ckanext.twitter.debug': True
            })
        tweeted, reason = twitter_api.post_tweet(u'This is a test tweet.',
                                                 self.data_factory().public_records[u'id'])
        eq_(tweeted, False)
        eq_(reason, u'debug')

    def test_shortens_author(self):
        # delete the config value so it's using the default
        self.config.remove([u'ckanext.twitter.new'])
        self.data_factory().destroy()
        self.data_factory().long_author()
        self.data_factory().create()
        pkg_dict = self.data_factory().public_records
        tweet_text = twitter_parsers.generate_tweet(self.data_factory().context,
                                                    pkg_dict[u'id'],
                                                    is_new=True)
        correct_tweet_text = u'New dataset: "A test package" by Dalton et al.' \
                             u' (5 records).'
        eq_(tweet_text, correct_tweet_text)
        self.data_factory().refresh()

    def test_shortens_title(self):
        # delete the config value so it's using the default
        self.config.remove([u'ckanext.twitter.new'])
        self.data_factory().destroy()
        self.data_factory().long_title()
        self.data_factory().create()
        pkg_dict = self.data_factory().public_records
        tweet_text = twitter_parsers.generate_tweet(self.data_factory().context,
                                                    pkg_dict[u'id'],
                                                    is_new=True)
        correct_tweet_text = u'New dataset: "This is a very long package ' \
                             u'title that\'s[...]" by Author (5 ' \
                             u'records).'
        eq_(tweet_text, correct_tweet_text)
        self.data_factory().refresh()

    def test_does_not_exceed_140_chars(self):
        # delete the config value so it's using the default
        self.config.remove([u'ckanext.twitter.new'])
        self.data_factory().destroy()
        self.data_factory().long_author()
        self.data_factory().long_title()
        self.data_factory().create()
        pkg_dict = self.data_factory().public_records
        force_truncate = twitter_parsers.generate_tweet(self.data_factory().context,
                                                        pkg_dict[u'id'],
                                                        is_new=True)
        no_force = twitter_parsers.generate_tweet(self.data_factory().context,
                                                  pkg_dict[u'id'],
                                                  is_new=True,
                                                  force_truncate=False)
        assert len(force_truncate) <= 140
        assert len(no_force) <= 140
        self.data_factory().refresh()

    def test_does_not_tweet_when_recently_tweeted(self):
        # make sure it can't send an actual tweet by removing the credentials
        cache_helpers.reset_cache()
        self.config.remove([u'ckanext.twitter.key', u'ckanext.twitter.secret',
                            u'ckanext.twitter.token_key',
                            u'ckanext.twitter.token_secret'])
        # turn off debug so it skips that check
        self.config.update({
            u'debug': False,
            u'ckanext.twitter.debug': False
            })
        # emulate successful tweet by manually inserting into the cache
        cache_helpers.cache(self.data_factory().public_records[u'id'])
        # try to tweet
        tweeted, reason = twitter_api.post_tweet(u'This is a test tweet.',
                                                 self.data_factory().public_records[u'id'])
        eq_(tweeted, False)
        eq_(reason, u'insufficient rest period')

    def test_does_tweet_when_new(self):
        # make sure it can't send an actual tweet by removing the credentials
        cache_helpers.reset_cache()
        self.config.remove([u'ckanext.twitter.key', u'ckanext.twitter.secret',
                            u'ckanext.twitter.token_key',
                            u'ckanext.twitter.token_secret'])
        # turn off debug so it skips that check
        self.config.update({
            u'debug': False,
            u'ckanext.twitter.debug': False
            })
        # refresh the database to see if it's sending tweets during creation
        self.data_factory().refresh()
        pkg_dict = self.data_factory().public_records
        # try to tweet
        tweeted, reason = twitter_api.post_tweet(u'This is a test tweet.',
                                                 pkg_dict[u'id'])
        eq_(tweeted, False)
        eq_(reason, u'not authenticated')
