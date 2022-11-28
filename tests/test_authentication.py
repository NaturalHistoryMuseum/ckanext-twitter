#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-twitter
# Created by the Natural History Museum in London, UK

from unittest.mock import patch, MagicMock

import pytest

from ckanext.twitter.lib import config_helpers
from ckanext.twitter.lib import twitter_api


@pytest.mark.ckan_config('ckanext.twitter.consumer_key', 'a-consumer-key')
@pytest.mark.ckan_config('ckanext.twitter.consumer_secret', 'a-consumer-secret')
@pytest.mark.ckan_config('ckanext.twitter.token_key', 'a-token-key')
@pytest.mark.ckan_config('ckanext.twitter.token_secret', 'a-token-secret')
def test_can_authenticate_success():
    mock_content = MagicMock()
    mock_response = MagicMock(status=200)
    mock_client = MagicMock(
        request=MagicMock(return_value=(mock_response, mock_content))
    )
    twitter_client_mock = MagicMock(return_value=mock_client)
    with patch('ckanext.twitter.lib.twitter_api.twitter_client', twitter_client_mock):
        is_authenticated = twitter_api.twitter_authenticate()
        assert is_authenticated


@pytest.mark.ckan_config('ckanext.twitter.consumer_key', 'a-consumer-key')
@pytest.mark.ckan_config('ckanext.twitter.consumer_secret', 'a-consumer-secret')
@pytest.mark.ckan_config('ckanext.twitter.token_key', 'a-token-key')
@pytest.mark.ckan_config('ckanext.twitter.token_secret', 'a-token-secret')
def test_can_authenticate_error():
    ck, cs, tk, ts = config_helpers.twitter_get_credentials()
    assert ck == 'a-consumer-key'
    assert cs == 'a-consumer-secret'
    assert tk == 'a-token-key'
    assert ts == 'a-token-secret'

    mock_content = MagicMock()
    mock_response = MagicMock(status=500)
    mock_client = MagicMock(
        request=MagicMock(return_value=(mock_response, mock_content))
    )
    twitter_client_mock = MagicMock(return_value=mock_client)
    with patch('ckanext.twitter.lib.twitter_api.twitter_client', twitter_client_mock):
        is_authenticated = twitter_api.twitter_authenticate()
        assert not is_authenticated


def test_can_authenticate_bad_creds():
    """
    Test what happens when we don't set any auth creds.
    """
    mock_content = MagicMock()
    mock_response = MagicMock(status=200)
    mock_client = MagicMock(
        request=MagicMock(return_value=(mock_response, mock_content))
    )
    twitter_client_mock = MagicMock(return_value=mock_client)
    with patch('ckanext.twitter.lib.twitter_api.twitter_client', twitter_client_mock):
        is_authenticated = twitter_api.twitter_authenticate()
        assert not is_authenticated
