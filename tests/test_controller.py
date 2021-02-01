#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-twitter
# Created by the Natural History Museum in London, UK

import json

import pytest
from ckan.plugins import toolkit
from ckan.tests import factories


@pytest.mark.filterwarnings(u'ignore::sqlalchemy.exc.SADeprecationWarning')
@pytest.mark.ckan_config(u'ckan.plugins', u'twitter')
@pytest.mark.ckan_config(u'ckanext.twitter.debug', True)
@pytest.mark.usefixtures(u'clean_db', u'with_plugins', u'with_request_context')
class TestController(object):

    def test_url_created(self):
        url = toolkit.url_for(u'tweet.send', package_id=u'not-a-real-id')
        assert url == u'/dataset/not-a-real-id/tweet'

    def test_url_ok(self, app):
        url = toolkit.url_for(u'tweet.send', package_id=u'not-a-real-id')
        response = app.post(url)
        assert response.status_code, 200

    def test_debug_post_tweet(self, app):
        dataset = factories.Dataset(
            notes=u'Test dataset'
        )
        url = toolkit.url_for(u'tweet.send', package_id=dataset[u'id'])
        response = app.post(url, data={u'tweet_text': u'this is a test tweet'})
        body = json.loads(response.body)
        assert body[u'reason'] == u'debug'
        assert body[u'tweet'] == u'this is a test tweet'
        assert not body[u'success']
