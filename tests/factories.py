"""Shared classes used in other tests. For generating test data"""
from itertools import cycle
from typing import List
from unittest.mock import Mock
from requests.models import Response


class RequestMockResponse:
    """A description of a http server response"""

    def __init__(self, text, response_code):
        """

        Parameters
        ----------
        text: str
            Text of this response
        response_code: int
            https response code, like 200 or 404
        """

        self.text = text
        self.response_code = response_code


class RequestsMock:
    """Can be put in place of the requests module. Can be set to return
    requests.models.Response objects
    """

    def __init__(self):
        self.requests = Mock()  # for keeping track of past requests
        self.http_methods = [
            self.requests.get,
            self.requests.post,
            self.requests.patch,
            self.requests.update,
        ]

    def set_response(self, response: RequestMockResponse):
        """Just for convenience"""
        self.set_responses([response])

    def set_responses(self, responses: List[RequestMockResponse]):
        """Any call to a http method will yield the given response. A list of responses will be looped over
        indefinitely

        Parameters
        ----------
        responses: List[RequestMockResponse]
            List of responses. Will be returned
        """

        objects = [
            self.create_response_object(response.response_code, response.text)
            for response in responses
        ]

        for method in self.http_methods:
            method.side_effect = cycle(objects)

    def set_response_exception(self, exception):
        """Any call to a http method will yield the given exception instance"""
        for method in self.http_methods:
            method.side_effect = exception

    @staticmethod
    def create_response_object(status_code, text):
        response = Response()
        response.encoding = "utf-8"
        response.status_code = status_code
        response._content = bytes(text, response.encoding)
        response.url = "mock_url"
        return response

    def get(self, *args, **kwargs):
        return self.requests.get(*args, **kwargs)

    def post(self, *args, **kwargs):
        return self.requests.post(*args, **kwargs)

    def reset(self):
        self.requests.reset_mock()

    def called(self):
        """True if any http method was called"""
        return any([x.called for x in self.http_methods])
