#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-twitter
# Created by the Natural History Museum in London, UK

import json

import nose
from ckantest.models import TestBase

from ckan.plugins import toolkit
from ckan.tests import factories


class TestController(TestBase):
    plugins = [u'twitter']
    persist = {
        u'ckanext.twitter.debug': True
        }

    def test_url_created(self):
        url = toolkit.url_for(u'tweet.send', package_id=u'not-a-real-id')
        nose.tools.assert_equal(url, '/dataset/not-a-real-id/tweet')

    def test_url_ok(self):
        url = toolkit.url_for(u'tweet.send', package_id=u'not-a-real-id')
        response = self.app.post(url)
        nose.tools.assert_equal(response.status_int, 200)

    def test_debug_post_tweet(self):
        dataset = factories.Dataset(
            notes=u'Test dataset'
            )
        url = toolkit.url_for(u'tweet.send', package_id=dataset[u'id'])
        response = self.app.post(url, {
            u'tweet_text': u'this is a test tweet'
            })
        body = json.loads(response.body)
        nose.tools.assert_equal(body[u'reason'], u'debug')
        nose.tools.assert_equal(body[u'tweet'], u'this is a test tweet')
        nose.tools.assert_equal(body[u'success'], False)
