#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-twitter
# Created by the Natural History Museum in London, UK
import pytest
from ckan.plugins import toolkit
from ckan.tests import factories
from ckan.tests.helpers import call_action
from mock import patch, MagicMock

from ckanext.twitter.lib import cache_helpers, parsers as twitter_parsers, twitter_api


@pytest.mark.filterwarnings(u'ignore::sqlalchemy.exc.SADeprecationWarning')
@pytest.mark.ckan_config(u'ckan.plugins', u'datastore')
@pytest.mark.usefixtures(u'clean_db', u'clean_datastore', u'with_plugins', u'with_request_context')
class TestTweetGeneration(object):

    def test_public(self):
        package = factories.Dataset()

        tweet_text = twitter_parsers.generate_tweet({}, package[u'id'], is_new=True)
        assert tweet_text is not None

    def test_private(self):
        # need an org to make a private package
        owner_org = factories.Organization()
        package = factories.Dataset(owner_org=owner_org[u'id'], private=True)

        # need to ignore the auth so that we can anonymously access the private package (we could
        # solve this by creating a user and adding them to the org above and then using that user
        # in the context, but this is easier tbh)
        context = {'ignore_auth': True}
        tweet_text = twitter_parsers.generate_tweet(context, package[u'id'], is_new=True)
        assert tweet_text is None

    @pytest.mark.ckan_config(u'ckanext.twitter.new', u'{{ title }} / {{ author }} / {{ records }}')
    def test_custom_new_text(self):
        title = u'A package title'
        author = u'Author'

        package = factories.Dataset(title=title, author=author)
        resource = factories.Resource(package_id=package[u'id'], url_type=u'datastore')

        records = [{u'x': i, u'y': u'number {}'.format(i)} for i in range(10)]
        call_action(u'datastore_create', resource_id=resource[u'id'], records=records)

        tweet_text = twitter_parsers.generate_tweet({}, package[u'id'], is_new=True)
        correct_tweet_text = u'{} / {} / {}'.format(title, author, len(records))
        assert tweet_text == correct_tweet_text

    def test_default_new_text(self):
        title = u'A package title'
        author = u'Author'

        package = factories.Dataset(title=title, author=author)
        resource = factories.Resource(package_id=package[u'id'], url_type=u'datastore')

        records = [{u'x': i, u'y': u'number {}'.format(i)} for i in range(10)]
        call_action(u'datastore_create', resource_id=resource[u'id'], records=records)

        tweet_text = twitter_parsers.generate_tweet({}, package[u'id'], is_new=True)
        correct_tweet_text = u'New dataset: "{}" by {} ({} records).'.format(title, author,
                                                                             len(records))
        assert tweet_text == correct_tweet_text

    @pytest.mark.ckan_config(u'ckanext.twitter.updated',
                             u'{{ title }} / {{ author }} / {{ records }}')
    def test_custom_updated_text(self):
        title = u'A package title'
        author = u'Author'

        package = factories.Dataset(title=title, author=author)
        resource = factories.Resource(package_id=package[u'id'], url_type=u'datastore')

        records = [{u'x': i, u'y': u'number {}'.format(i)} for i in range(10)]
        call_action(u'datastore_create', resource_id=resource[u'id'], records=records)

        tweet_text = twitter_parsers.generate_tweet({}, package[u'id'], is_new=False)
        correct_tweet_text = u'{} / {} / {}'.format(title, author, len(records))
        assert tweet_text == correct_tweet_text

    def test_default_updated_text(self):
        title = u'A package title'
        author = u'Author'

        package = factories.Dataset(title=title, author=author)
        resource = factories.Resource(package_id=package[u'id'], url_type=u'datastore')

        records = [{u'x': i, u'y': u'number {}'.format(i)} for i in range(10)]
        call_action(u'datastore_create', resource_id=resource[u'id'], records=records)

        tweet_text = twitter_parsers.generate_tweet({}, package[u'id'], is_new=False)
        correct_tweet_text = u'Updated dataset: "{}" by {} ({} records).'.format(title, author,
                                                                                 len(records))
        assert tweet_text == correct_tweet_text

    @pytest.mark.ckan_config(u'ckanext.twitter.debug', True)
    def test_does_not_tweet_when_debug(self):
        tweeted, reason = twitter_api.post_tweet(u'Mock text', MagicMock())
        assert not tweeted
        assert reason == u'debug'

    def test_shortens_author(self):
        title = u'A package title'
        author = u'Captain Author; Captain Author2; Captain Author3'

        package = factories.Dataset(title=title, author=author)

        tweet_text = twitter_parsers.generate_tweet({}, package[u'id'], is_new=True)
        correct_tweet_text = u'New dataset: "{}" by {} et al. (0 resource).'.format(title,
                                                                                    u'Author')
        assert tweet_text == correct_tweet_text

    def test_shortens_title(self):
        title = u'A package title that is pretty long but not ridiculously long, woo!'
        author = u'Captain Author'

        package = factories.Dataset(title=title, author=author)

        tweet_text = twitter_parsers.generate_tweet({}, package[u'id'], is_new=True)
        correct_tweet_text = u'New dataset: "{}[...]" by {} (0 resource).'.format(title[:43],
                                                                                  u'Author')
        assert tweet_text == correct_tweet_text

    def test_does_not_exceed_140_chars(self):
        title = u'A package title that is pretty long but not ridiculously long, woo!'
        author = u'; '.join(u'Captain Author{}'.format(i) for i in range(40))

        package = factories.Dataset(title=title, author=author)

        force_truncate = twitter_parsers.generate_tweet({}, package[u'id'], is_new=True)
        no_force = twitter_parsers.generate_tweet({}, package[u'id'], is_new=True,
                                                  force_truncate=False)
        assert len(force_truncate) <= 140
        assert len(no_force) <= 140

    def test_does_not_tweet_when_recently_tweeted(self):
        # mock the expires function to always return that the mock package id we send in hasn't
        # expired yet
        mock_cache_helpers = MagicMock(expired=MagicMock(return_value=False))
        with patch(u'ckanext.twitter.lib.twitter_api.cache_helpers', mock_cache_helpers):
            tweeted, reason = twitter_api.post_tweet(u'This is a test tweet.', MagicMock())
        assert not tweeted
        assert reason == u'insufficient rest period'

    def test_does_tweet_when_not_recently_tweeted(self):
        # this test also confirms the auth check works...

        mock_cache_helpers = MagicMock(expired=MagicMock(return_value=True))
        with patch(u'ckanext.twitter.lib.twitter_api.cache_helpers', mock_cache_helpers):
            tweeted, reason = twitter_api.post_tweet(u'This is a test tweet.', MagicMock())

        assert not tweeted
        assert reason == u'not authenticated'
