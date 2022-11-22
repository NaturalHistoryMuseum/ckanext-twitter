#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-twitter
# Created by the Natural History Museum in London, UK

import json

import pytest
from ckan.plugins import toolkit
from ckan.tests import factories


@pytest.mark.filterwarnings('ignore::sqlalchemy.exc.SADeprecationWarning')
@pytest.mark.ckan_config('ckan.plugins', 'twitter')
@pytest.mark.ckan_config('ckanext.twitter.debug', True)
@pytest.mark.usefixtures('clean_db', 'with_plugins', 'with_request_context')
class TestController(object):
    def test_url_created(self):
        url = toolkit.url_for('tweet.send', package_id='not-a-real-id')
        assert url == '/dataset/not-a-real-id/tweet'

    def test_url_ok(self, app):
        url = toolkit.url_for('tweet.send', package_id='not-a-real-id')
        response = app.post(url)
        assert response.status_code, 200

    def test_debug_post_tweet(self, app):
        dataset = factories.Dataset(notes='Test dataset')
        url = toolkit.url_for('tweet.send', package_id=dataset['id'])
        response = app.post(url, data={'tweet_text': 'this is a test tweet'})
        body = json.loads(response.body)
        assert body['reason'] == 'debug'
        assert body['tweet'] == 'this is a test tweet'
        assert not body['success']
