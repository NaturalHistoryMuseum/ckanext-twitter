from unittest.mock import patch, call, MagicMock

import pytest
from ckan.plugins import toolkit


class MockSession(dict):
    def __init__(self):
        super().__init__()
        self.save = MagicMock()


@pytest.mark.filterwarnings('ignore::sqlalchemy.exc.SADeprecationWarning')
@pytest.mark.ckan_config('ckan.plugins', 'twitter')
@pytest.mark.usefixtures('clean_db', 'with_plugins', 'with_request_context')
def test_clear(app):
    package_id = u'some-package-id'
    url = toolkit.url_for('tweet.clear', package_id=package_id)

    mock_cache_helpers = MagicMock()
    mock_session = MockSession()
    mock_session['twitter_is_suitable'] = package_id

    with patch(u'ckanext.twitter.routes.tweet.session', mock_session):
        with patch(u'ckanext.twitter.routes.tweet.cache_helpers', mock_cache_helpers):
            app.post(url)

    assert mock_cache_helpers.remove_from_cache.call_args == call(package_id)
    assert 'twitter_is_suitable' not in mock_session
    assert mock_session.save.called


@pytest.mark.filterwarnings('ignore::sqlalchemy.exc.SADeprecationWarning')
@pytest.mark.ckan_config('ckan.plugins', 'twitter')
@pytest.mark.usefixtures('clean_db', 'with_plugins', 'with_request_context')
def test_clear_session_is_empty(app):
    package_id = u'some-package-id'
    url = toolkit.url_for('tweet.clear', package_id=package_id)

    mock_cache_helpers = MagicMock()
    mock_session = MockSession()

    with patch(u'ckanext.twitter.routes.tweet.session', mock_session):
        with patch(u'ckanext.twitter.routes.tweet.cache_helpers', mock_cache_helpers):
            app.post(url)

    assert mock_cache_helpers.remove_from_cache.call_args == call(package_id)
    assert 'twitter_is_suitable' not in mock_session
    assert not mock_session.save.called
