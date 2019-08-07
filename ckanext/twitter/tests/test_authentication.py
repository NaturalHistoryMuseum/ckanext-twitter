#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-twitter
# Created by the Natural History Museum in London, UK

import nose
from ckantest.models import TestBase

import ckanext.twitter.lib.config_helpers
from ckanext.twitter.lib import twitter_api

eq_ = nose.tools.eq_


class TestTwitterAuthentication(TestBase):
    plugins = [u'twitter']
    persist = {
        u'ckanext.twitter.debug': True
        }

    def test_can_authenticate(self):
        ck, cs, tk, ts = ckanext.twitter.lib.config_helpers \
            .twitter_get_credentials()
        is_authenticated = twitter_api.twitter_authenticate()
        eq_(is_authenticated, True,
            u'Authentication not successful.')
