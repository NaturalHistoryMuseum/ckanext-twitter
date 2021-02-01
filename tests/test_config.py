#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-twitter
# Created by the Natural History Museum in London, UK

import ckanext.twitter.lib.config_helpers as config_helpers
import pytest


@pytest.mark.ckan_config(u'ckanext.twitter.debug', True)
def test_gets_debug_value_when_present():
    assert config_helpers.twitter_is_debug()


@pytest.mark.ckan_config(u'ckanext.twitter.debug', False)
def test_gets_debug_value_when_present_even_if_false():
    assert not config_helpers.twitter_is_debug()


@pytest.mark.ckan_config(u'debug', True)
def test_gets_debug_default_when_absent():
    assert config_helpers.twitter_is_debug()


@pytest.mark.ckan_config(u'ckanext.twitter.hours_between_tweets', 2)
def test_gets_hours_between_tweets_value_when_present():
    assert config_helpers.twitter_hours_between_tweets() == 2


def test_gets_hours_between_tweets_default_when_absent():
    assert config_helpers.twitter_hours_between_tweets() == 24


@pytest.mark.ckan_config(u'ckanext.twitter.consumer_key', u'a-consumer-key')
@pytest.mark.ckan_config(u'ckanext.twitter.consumer_secret', u'a-consumer-secret')
@pytest.mark.ckan_config(u'ckanext.twitter.token_key', u'a-token-key')
@pytest.mark.ckan_config(u'ckanext.twitter.token_secret', u'a-token-secret')
def test_twitter_get_credentials():
    ck, cs, tk, ts = config_helpers.twitter_get_credentials()
    assert ck == u'a-consumer-key'
    assert cs == u'a-consumer-secret'
    assert tk == u'a-token-key'
    assert ts == u'a-token-secret'


def test_twitter_get_credentials_defaults():
    ck, cs, tk, ts = config_helpers.twitter_get_credentials()
    assert ck == u'no-consumer-key-set'
    assert cs == u'no-consumer-secret-set'
    assert tk == u'no-token-key-set'
    assert ts == u'no-token-secret-set'


@pytest.mark.ckan_config(u'ckanext.twitter.disable_edit', True)
def test_gets_disable_edit_value_when_present():
    assert config_helpers.twitter_disable_edit()


def test_gets_disable_edit_default_when_absent():
    assert not config_helpers.twitter_disable_edit()
