#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-twitter
# Created by the Natural History Museum in London, UK

import pytest
from ckan.tests import factories
from ckan.tests.helpers import call_action
from unittest.mock import patch

from ckanext.twitter.lib import parsers as twitter_parsers


@pytest.mark.filterwarnings('ignore::sqlalchemy.exc.SADeprecationWarning')
@pytest.mark.ckan_config('ckan.plugins', 'datastore twitter')
@pytest.mark.ckan_config('ckanext.twitter.debug', True)
@pytest.mark.usefixtures(
    'clean_db', 'clean_datastore', 'with_plugins', 'with_request_context'
)
@patch('ckanext.twitter.plugin.session')
class TestDatasetMetadata(object):
    def test_gets_dataset_number_of_records_if_has_records(self, mock_session):
        package = factories.Dataset()
        resource = factories.Resource(package_id=package['id'], url_type='datastore')

        records = [{'x': i, 'y': 'number {}'.format(i)} for i in range(10)]
        call_action('datastore_create', resource_id=resource['id'], records=records)

        record_count = twitter_parsers.get_number_records({}, package['id'])
        assert record_count == len(records)

    def test_gets_dataset_number_of_records_if_no_records(self, mock_session):
        package = factories.Dataset()
        resource = factories.Resource(package_id=package['id'], url_type='datastore')

        record_count = twitter_parsers.get_number_records({}, package['id'])
        assert record_count == 0
