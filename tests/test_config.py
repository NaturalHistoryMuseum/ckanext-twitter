#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-twitter
# Created by the Natural History Museum in London, UK

import pytest

import ckanext.twitter.lib.config_helpers as config_helpers


@pytest.mark.ckan_config('ckanext.twitter.debug', True)
def test_gets_debug_value_when_present():
    assert config_helpers.twitter_is_debug()


@pytest.mark.ckan_config('ckanext.twitter.debug', False)
def test_gets_debug_value_when_present_even_if_false():
    assert not config_helpers.twitter_is_debug()


@pytest.mark.ckan_config('debug', True)
def test_gets_debug_default_when_absent():
    assert config_helpers.twitter_is_debug()


@pytest.mark.ckan_config('ckanext.twitter.hours_between_tweets', 2)
def test_gets_hours_between_tweets_value_when_present():
    assert config_helpers.twitter_hours_between_tweets() == 2


def test_gets_hours_between_tweets_default_when_absent():
    assert config_helpers.twitter_hours_between_tweets() == 24


@pytest.mark.ckan_config('ckanext.twitter.consumer_key', 'a-consumer-key')
@pytest.mark.ckan_config('ckanext.twitter.consumer_secret', 'a-consumer-secret')
@pytest.mark.ckan_config('ckanext.twitter.token_key', 'a-token-key')
@pytest.mark.ckan_config('ckanext.twitter.token_secret', 'a-token-secret')
def test_twitter_get_credentials():
    ck, cs, tk, ts = config_helpers.twitter_get_credentials()
    assert ck == 'a-consumer-key'
    assert cs == 'a-consumer-secret'
    assert tk == 'a-token-key'
    assert ts == 'a-token-secret'


def test_twitter_get_credentials_defaults():
    ck, cs, tk, ts = config_helpers.twitter_get_credentials()
    assert ck == 'no-consumer-key-set'
    assert cs == 'no-consumer-secret-set'
    assert tk == 'no-token-key-set'
    assert ts == 'no-token-secret-set'


@pytest.mark.ckan_config('ckanext.twitter.disable_edit', True)
def test_gets_disable_edit_value_when_present():
    assert config_helpers.twitter_disable_edit()


def test_gets_disable_edit_default_when_absent():
    assert not config_helpers.twitter_disable_edit()
