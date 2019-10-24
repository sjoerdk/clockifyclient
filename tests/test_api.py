#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

from clockifyclient.api import APIServer, APIServerException
from tests.factories import ClockifyMockResponses


@pytest.fixture()
def a_server():
    return APIServer("localhost")


def test_api_key_missing(mock_requests, a_server):
    """Calling API with wrong or missing api key should yield helpful exception"""
    mock_requests.set_response(ClockifyMockResponses.AUTH_ERROR)

    with pytest.raises(APIServerException):
        a_server.get("/test", 'test_api_key')


@pytest.mark.parametrize('mock_response', [ClockifyMockResponses.GET_WORKSPACES,
                                           ClockifyMockResponses.GET_USER,
                                           ClockifyMockResponses.GET_PROJECTS])
def test_get_ok(mock_requests, a_server, mock_response):
    """No exceptions should be raised by normal calls"""

    mock_requests.set_response(mock_response)
    a_server.get(path='/mock_path', api_key="mock_key")


def test_post_ok(mock_requests, a_server):
    """No exceptions should be raised for this """

    mock_requests.set_response(ClockifyMockResponses.POST_TIME_ENTRY)
    a_server.post(path='/workspaces/12345/time-entries', api_key="mock_key", data={'test': 'some_value'})
