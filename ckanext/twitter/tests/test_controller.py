#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-twitter
# Created by the Natural History Museum in London, UK

import json

import ckantest.factories
import ckantest.helpers
import nose

from ckan import plugins
from ckan.plugins import toolkit
from ckan.tests import factories, helpers

eq_ = nose.tools.eq_


class TestController(object):
    @classmethod
    def setup_class(cls):
        cls.config = ckantest.helpers.Configurer()
        cls.app = helpers._get_test_app()
        plugins.load(u'twitter')

    @classmethod
    def teardown_class(cls):
        cls.config.reset()
        plugins.unload(u'twitter')
        helpers.reset_db()

    def test_url_created(self):
        url = toolkit.url_for(u'post_tweet', pkg_id=u'not-a-real-id')
        eq_(url, '/dataset/not-a-real-id/tweet')

    def test_url_ok(self):
        url = toolkit.url_for(u'post_tweet', pkg_id=u'not-a-real-id')
        response = self.app.post(url)
        eq_(response.status_int, 200)

    def test_debug_post_tweet(self):
        dataset = factories.Dataset(
            notes=u'Test dataset'
            )
        url = toolkit.url_for(u'post_tweet', pkg_id=dataset[u'id'])
        response = self.app.post(url, {
            u'tweet_text': u'this is a test tweet'
            })
        body = json.loads(response.body)
        eq_(body[u'reason'], u'debug')
        eq_(body[u'tweet'], u'this is a test tweet')
        eq_(body[u'success'], False)
