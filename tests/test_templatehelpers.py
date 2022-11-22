#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-twitter
# Created by the Natural History Museum in London, UK
from unittest.mock import patch, MagicMock, call

import pytest
from ckan.model import State
from ckan.tests import factories
from ckan.tests.helpers import call_action

from ckanext.twitter.lib.helpers import TwitterJSHelpers, twitter_pkg_suitable


@pytest.fixture
def js_helpers():
    return TwitterJSHelpers()


@pytest.fixture
def session():
    return {}


class TestGetConfigVariables(object):
    def test_returns_false_if_not_in_session(self, js_helpers, session):
        package = factories.Dataset()

        with patch('ckanext.twitter.lib.helpers.session', session):
            assert not js_helpers.tweet_ready(package['id'])

    def test_returns_true_if_is_in_session(self, js_helpers, session):
        package = factories.Dataset()
        session['twitter_is_suitable'] = package['id']

        with patch('ckanext.twitter.lib.helpers.session', session):
            assert js_helpers.tweet_ready(package['id'])

    @pytest.mark.filterwarnings('ignore::sqlalchemy.exc.SADeprecationWarning')
    @pytest.mark.usefixtures('clean_db', 'with_request_context')
    def test_gets_tweet(self, js_helpers):
        package = factories.Dataset()

        mock_parsers = MagicMock()

        with patch('ckanext.twitter.lib.helpers.twitter_parsers', mock_parsers):
            js_helpers.get_tweet(package['id'])

        assert mock_parsers.generate_tweet.call_args == call({}, package['id'], True)

    @pytest.mark.filterwarnings('ignore::sqlalchemy.exc.SADeprecationWarning')
    @pytest.mark.usefixtures('clean_db', 'with_request_context')
    def test_gets_tweet_old_package(self, js_helpers):
        package = factories.Dataset()
        for i in range(10):
            call_action('package_patch', id=package['id'], notes=f'Note number {i}')

        mock_parsers = MagicMock()

        with patch('ckanext.twitter.lib.helpers.twitter_parsers', mock_parsers):
            js_helpers.get_tweet(package['id'])

        assert mock_parsers.generate_tweet.call_args == call({}, package['id'], False)

    @pytest.mark.filterwarnings('ignore::sqlalchemy.exc.SADeprecationWarning')
    @pytest.mark.usefixtures('clean_db', 'with_request_context')
    def test_not_suitable_if_does_not_exist(self):
        is_suitable = twitter_pkg_suitable({}, 'not-a-real-id')
        assert not is_suitable

    @pytest.mark.filterwarnings('ignore::sqlalchemy.exc.SADeprecationWarning')
    @pytest.mark.usefixtures('clean_db', 'with_request_context')
    def test_not_suitable_if_not_active(self):
        package = factories.Dataset(state='inactive')
        context = {'ignore_auth': True}
        is_suitable = twitter_pkg_suitable(context, package['id'])
        assert not is_suitable

    @pytest.mark.filterwarnings('ignore::sqlalchemy.exc.SADeprecationWarning')
    @pytest.mark.usefixtures('clean_db', 'with_request_context')
    def test_not_suitable_if_no_resources(self):
        package = factories.Dataset(state=State.ACTIVE)

        is_suitable = twitter_pkg_suitable({}, package['id'])
        assert not is_suitable

    @pytest.mark.filterwarnings('ignore::sqlalchemy.exc.SADeprecationWarning')
    @pytest.mark.usefixtures('clean_db', 'with_request_context')
    def test_not_suitable_if_no_active_resources(self):
        package = factories.Dataset(state=State.ACTIVE)
        resource = factories.Resource(package_id=package['id'])
        call_action('resource_delete', id=resource['id'])
        context = {'ignore_auth': True}
        is_suitable = twitter_pkg_suitable(context, package['id'])
        assert not is_suitable

    @pytest.mark.filterwarnings('ignore::sqlalchemy.exc.SADeprecationWarning')
    @pytest.mark.usefixtures('clean_db', 'with_request_context')
    def test_not_suitable_if_private(self):
        # need an org to make a private package
        owner_org = factories.Organization()
        package = factories.Dataset(owner_org=owner_org['id'], private=True)
        factories.Resource(package_id=package['id'])

        # need to ignore the auth so that we can anonymously access the private package (we could
        # solve this by creating a user and adding them to the org above and then using that user
        # in the context, but this is easier tbh)
        context = {'ignore_auth': True}

        is_suitable = twitter_pkg_suitable(context, package['id'])
        assert not is_suitable

    @pytest.mark.filterwarnings('ignore::sqlalchemy.exc.SADeprecationWarning')
    @pytest.mark.usefixtures('clean_db', 'with_request_context')
    def test_otherwise_suitable(self):
        # need an org to make a private package
        package = factories.Dataset()
        factories.Resource(package_id=package['id'])
        factories.Resource(package_id=package['id'])
        factories.Resource(package_id=package['id'])
        factories.Resource(package_id=package['id'])

        is_suitable = twitter_pkg_suitable({}, package['id'])
        assert is_suitable
