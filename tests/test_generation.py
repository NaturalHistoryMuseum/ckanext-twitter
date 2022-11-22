#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-twitter
# Created by the Natural History Museum in London, UK
from unittest.mock import patch, MagicMock

import pytest
from ckan.tests import factories
from ckan.tests.helpers import call_action

from ckanext.twitter.lib import parsers as twitter_parsers, twitter_api


@pytest.mark.filterwarnings('ignore::sqlalchemy.exc.SADeprecationWarning')
@pytest.mark.ckan_config('ckan.plugins', 'datastore')
@pytest.mark.usefixtures(
    'clean_db', 'clean_datastore', 'with_plugins', 'with_request_context'
)
class TestTweetGeneration(object):
    def test_public(self):
        package = factories.Dataset()

        tweet_text = twitter_parsers.generate_tweet({}, package['id'], is_new=True)
        assert tweet_text is not None

    def test_private(self):
        # need an org to make a private package
        owner_org = factories.Organization()
        package = factories.Dataset(owner_org=owner_org['id'], private=True)

        # need to ignore the auth so that we can anonymously access the private package (we could
        # solve this by creating a user and adding them to the org above and then using that user
        # in the context, but this is easier tbh)
        context = {'ignore_auth': True}
        tweet_text = twitter_parsers.generate_tweet(context, package['id'], is_new=True)
        assert tweet_text is None

    @pytest.mark.ckan_config(
        'ckanext.twitter.new', '{{ title }} / {{ author }} / {{ records }}'
    )
    def test_custom_new_text(self):
        title = 'A package title'
        author = 'Author'

        package = factories.Dataset(title=title, author=author)
        resource = factories.Resource(package_id=package['id'], url_type='datastore')

        records = [{'x': i, 'y': f'number {i}'} for i in range(10)]
        call_action('datastore_create', resource_id=resource['id'], records=records)

        tweet_text = twitter_parsers.generate_tweet({}, package['id'], is_new=True)
        correct_tweet_text = f'{title} / {author} / {len(records)}'
        assert tweet_text == correct_tweet_text

    def test_default_new_text(self):
        title = 'A package title'
        author = 'Author'

        package = factories.Dataset(title=title, author=author)
        resource = factories.Resource(package_id=package['id'], url_type='datastore')

        records = [{'x': i, 'y': f'number {i}'} for i in range(10)]
        call_action('datastore_create', resource_id=resource['id'], records=records)

        tweet_text = twitter_parsers.generate_tweet({}, package['id'], is_new=True)
        correct_tweet_text = (
            f'New dataset: "{title}" by {author} ({len(records)} records).'
        )
        assert tweet_text == correct_tweet_text

    @pytest.mark.ckan_config(
        'ckanext.twitter.updated', '{{ title }} / {{ author }} / {{ records }}'
    )
    def test_custom_updated_text(self):
        title = 'A package title'
        author = 'Author'

        package = factories.Dataset(title=title, author=author)
        resource = factories.Resource(package_id=package['id'], url_type='datastore')

        records = [{'x': i, 'y': f'number {i}'} for i in range(10)]
        call_action('datastore_create', resource_id=resource['id'], records=records)

        tweet_text = twitter_parsers.generate_tweet({}, package['id'], is_new=False)
        correct_tweet_text = f'{title} / {author} / {len(records)}'
        assert tweet_text == correct_tweet_text

    def test_default_updated_text(self):
        title = 'A package title'
        author = 'Author'

        package = factories.Dataset(title=title, author=author)
        resource = factories.Resource(package_id=package['id'], url_type='datastore')

        records = [{'x': i, 'y': f'number {i}'} for i in range(10)]
        call_action('datastore_create', resource_id=resource['id'], records=records)

        tweet_text = twitter_parsers.generate_tweet({}, package['id'], is_new=False)
        correct_tweet_text = (
            f'Updated dataset: "{title}" by {author} ({len(records)} records).'
        )
        assert tweet_text == correct_tweet_text

    @pytest.mark.ckan_config('ckanext.twitter.debug', True)
    def test_does_not_tweet_when_debug(self):
        tweeted, reason = twitter_api.post_tweet('Mock text', MagicMock())
        assert not tweeted
        assert reason == 'debug'

    def test_shortens_author(self):
        title = 'A package title'
        author = 'Captain Author; Captain Author2; Captain Author3'

        package = factories.Dataset(title=title, author=author)

        tweet_text = twitter_parsers.generate_tweet({}, package['id'], is_new=True)
        correct_tweet_text = f'New dataset: "{title}" by Author et al. (0 resource).'
        assert tweet_text == correct_tweet_text

    def test_shortens_title(self):
        title = 'A package title that is pretty long but not ridiculously long, woo!'
        author = 'Captain Author'

        package = factories.Dataset(title=title, author=author)

        tweet_text = twitter_parsers.generate_tweet({}, package['id'], is_new=True)
        correct_tweet_text = f'New dataset: "{title[:43]}[...]" by Author (0 resource).'
        assert tweet_text == correct_tweet_text

    def test_does_not_exceed_140_chars(self):
        title = 'A package title that is pretty long but not ridiculously long, woo!'
        author = '; '.join(f'Captain Author{i}' for i in range(40))

        package = factories.Dataset(title=title, author=author)

        force_truncate = twitter_parsers.generate_tweet({}, package['id'], is_new=True)
        no_force = twitter_parsers.generate_tweet(
            {}, package['id'], is_new=True, force_truncate=False
        )
        assert len(force_truncate) <= 140
        assert len(no_force) <= 140

    @pytest.mark.ckan_config('debug', False)
    @pytest.mark.ckan_config('ckanext.twitter.debug', False)
    def test_does_not_tweet_when_recently_tweeted(self):
        # mock the expires function to always return that the mock package id we send in hasn't
        # expired yet
        mock_cache_helpers = MagicMock(expired=MagicMock(return_value=False))
        with patch('ckanext.twitter.lib.twitter_api.cache_helpers', mock_cache_helpers):
            tweeted, reason = twitter_api.post_tweet(
                'This is a test tweet.', MagicMock()
            )
        assert not tweeted
        assert reason == 'insufficient rest period'

    @pytest.mark.ckan_config('debug', False)
    @pytest.mark.ckan_config('ckanext.twitter.debug', False)
    def test_does_tweet_when_not_recently_tweeted(self):
        # this test also confirms the auth check works...

        mock_cache_helpers = MagicMock(expired=MagicMock(return_value=True))
        with patch('ckanext.twitter.lib.twitter_api.cache_helpers', mock_cache_helpers):
            tweeted, reason = twitter_api.post_tweet(
                'This is a test tweet.', MagicMock()
            )

        assert not tweeted
        assert reason == 'not authenticated'
