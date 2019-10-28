#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
import requests

from clockifyclient.api import APIServer, APIServerException
from clockifyclient.exceptions import ClockifyClientException
from tests.factories import ClockifyMockResponses, RequestMockResponse


@pytest.fixture()
def a_server():
    return APIServer("localhost")


def test_api_key_missing(mock_requests, a_server):
    """Calling API with wrong or missing api key should yield helpful exception"""
    mock_requests.set_response(ClockifyMockResponses.AUTH_ERROR)

    with pytest.raises(APIServerException):
        a_server.get("/test", "test_api_key")


@pytest.mark.parametrize(
    "mock_response",
    [
        ClockifyMockResponses.GET_WORKSPACES,
        ClockifyMockResponses.GET_USER,
        ClockifyMockResponses.GET_PROJECTS,
    ],
)
def test_get_ok(mock_requests, a_server, mock_response):
    """No exceptions should be raised by normal calls"""

    mock_requests.set_response(mock_response)
    a_server.get(path="/mock_path", api_key="mock_key")


def test_post_ok(mock_requests, a_server):
    """No exceptions should be raised for this """

    mock_requests.set_response(ClockifyMockResponses.POST_TIME_ENTRY)
    a_server.post(
        path="/workspaces/12345/time-entries",
        api_key="mock_key",
        data={"test": "some_value"},
    )


def test_requests_error(mock_requests, a_server):
    """Calling a non-existent server for example"""
    mock_requests.set_response_exception(
        requests.exceptions.ConnectionError("Mocked connection error")
    )

    with pytest.raises(ClockifyClientException):
        a_server.get("/test", "test_api_key")


@pytest.mark.parametrize(
    "response_text, response_code",
    [
        (
            '{"something":"Full authentication is required to access this resource","code":1000}',
            401,
        ),
        (
            '{"message":"A message and error http error, but no error code in json","forgot_code":0}',
            401,
        ),
        ("not even json", 401),
        ("{}", 401),
    ],
)
def test_incongruous_responses(mock_requests, a_server, response_text, response_code):
    """Weird stuff coming from server should all result in ClockifyClientExceptions"""

    mock_requests.set_response(RequestMockResponse(response_text, response_code))

    with pytest.raises(ClockifyClientException) as e:
        a_server.get("/test", "test_api_key")
