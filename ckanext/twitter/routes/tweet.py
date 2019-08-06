#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-twitter
# Created by the Natural History Museum in London, UK

import json

from flask import Blueprint

from ckan.common import session
from ckan.plugins import toolkit
from ckanext.twitter.lib import cache_helpers, twitter_api

blueprint = Blueprint(name=u'tweet', import_name=__name__)


@blueprint.route(u'/dataset/<package_id>/tweet', methods=[u'POST'])
def send(package_id):
    '''
    Posts the tweet given in the request body. The package ID is
    required for caching. Returns json data for displaying success/error
    messages.
    :param package_id: The package ID (for caching).
    :return: str
    '''
    body = dict(toolkit.request.postvars)
    text = body.get(u'tweet_text', None)
    if text:
        posted, reason = twitter_api.post_tweet(text, package_id)
    else:
        posted = False
        reason = u'no tweet defined'
    return json.dumps({
        u'success': posted,
        u'reason': reason,
        u'tweet': text if text else u'tweet not defined'
        })


@blueprint.route('/dataset/<package_id>/tweet-clear', methods=[u'POST'])
def clear(package_id):
    cache_helpers.remove_from_cache(package_id)
    if u'twitter_is_suitable' in session:
        del session[u'twitter_is_suitable']
        session.save()
    return ''
