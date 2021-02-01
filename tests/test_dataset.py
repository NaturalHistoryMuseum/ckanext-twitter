#!/usr/bin/env python
# encoding: utf-8
#
# This file is part of ckanext-twitter
# Created by the Natural History Museum in London, UK

import pytest
from ckan.plugins import toolkit
from ckan.tests import factories
from ckan.tests.helpers import call_action
from ckanext.twitter.lib import (parsers as twitter_parsers)
from mock import patch


@pytest.mark.filterwarnings(u'ignore::sqlalchemy.exc.SADeprecationWarning')
@pytest.mark.ckan_config(u'ckan.plugins', u'datastore twitter')
@pytest.mark.ckan_config(u'ckanext.twitter.debug', True)
@pytest.mark.usefixtures(u'clean_db', u'clean_datastore', u'with_plugins', u'with_request_context')
@patch(u'ckanext.twitter.plugin.session')
class TestDatasetMetadata(object):

    def test_gets_dataset_number_of_records_if_has_records(self, mock_session):
        package = factories.Dataset()
        resource = factories.Resource(package_id=package[u'id'], url_type=u'datastore')

        records = [{u'x': i, u'y': u'number {}'.format(i)} for i in range(10)]
        call_action(u'datastore_create', resource_id=resource[u'id'], records=records)

        record_count = twitter_parsers.get_number_records({}, package[u'id'])
        assert record_count == len(records)

    def test_gets_dataset_number_of_records_if_no_records(self, mock_session):
        package = factories.Dataset()
        resource = factories.Resource(package_id=package[u'id'], url_type=u'datastore')

        record_count = twitter_parsers.get_number_records({}, package[u'id'])
        assert record_count == 0
