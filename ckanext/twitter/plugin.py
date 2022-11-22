#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-twitter
# Created by the Natural History Museum in London, UK

from beaker.cache import cache_regions
from ckan.common import session
from ckan.plugins import SingletonPlugin, implements, interfaces, toolkit

import ckanext.twitter.lib.config_helpers
from ckanext.twitter import routes
from ckanext.twitter.lib import config_helpers, helpers as twitter_helpers


class TwitterPlugin(SingletonPlugin):
    """
    Automatically send tweets when a dataset is updated or created.
    """

    implements(interfaces.IConfigurable, inherit=True)
    implements(interfaces.IConfigurer)
    implements(interfaces.IPackageController, inherit=True)
    implements(interfaces.ITemplateHelpers, inherit=True)
    implements(interfaces.IBlueprint, inherit=True)

    # IConfigurable
    def configure(self, config):
        cache_regions.update(
            {
                'twitter': {
                    'expire': ckanext.twitter.lib.config_helpers.twitter_hours_between_tweets(),
                    'type': 'memory',
                    'enabled': True,
                    'key_length': 250,
                }
            }
        )

    # IConfigurer
    def update_config(self, config):
        # Add templates
        toolkit.add_template_directory(config, 'theme/templates')
        # Add resources
        toolkit.add_resource('theme/assets', 'ckanext-twitter')

    # IPackageController
    def after_update(self, context, pkg_dict):
        is_suitable = twitter_helpers.twitter_pkg_suitable(context, pkg_dict['id'])
        if is_suitable:
            session.setdefault('twitter_is_suitable', pkg_dict['id'])
            session.save()

    # ITemplateHelpers
    def get_helpers(self):
        js_helpers = twitter_helpers.TwitterJSHelpers()
        return {
            'tweet_ready': js_helpers.tweet_ready,
            'get_tweet': js_helpers.get_tweet,
            'disable_edit': config_helpers.twitter_disable_edit,
        }

    ## IBlueprint
    def get_blueprint(self):
        return routes.blueprints
