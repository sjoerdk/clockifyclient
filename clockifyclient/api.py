"""Models the clockify API. Tries to stay close to the actual endpoints.
This layer is the only one that should do actual http queries
"""
from collections import Iterator
from json.decoder import JSONDecodeError
from typing import Dict, List

import requests

from clockifyclient.decorators import except_connection_error
from clockifyclient.exceptions import ClockifyClientException


class APIServer:
    """Models a clockify API server. Basic HTTP interaction. Returns json and
    raises exceptions

    Notes
    -----
    For higher level interactions, see client.ClockifyAPI
    """

    def __init__(self, url):
        """

        Parameters
        ----------
        url: str
            url of the api
        """
        self.url = url

    @except_connection_error
    def get(self, path, api_key, params=None):
        """

        Parameters
        ----------
        path: str
            relative path to endpoint. Like '/user' or '/workspaces'
        api_key: str
            api key to send with request
        params: Dict, optional
            Request parameters to send. Defaults to empty list


        Returns
        -------
        Dict or List:
            Json-interpreted response from server

        """
        if not params:
            params = {}
        response_raw = requests.get(
            self.url + path,
            headers={"X-Api-key": api_key, "content-type": "application/json"},
            params=params
        )
        return APIRawResponse(response_raw).parse()

    def get_iterator(self, path, api_key, params=None) -> 'PagedGetIterator':
        """A get request that iterates over items and calls API again for more
        items if needed

        Parameters
        ----------
        path: str
            relative path to endpoint. Like '/user' or '/workspaces'
        api_key: str
            api key to send with request
        params: Dict, optional
            Request parameters to send. Defaults to empty list


        Returns
        -------
        PagedGetIterator
            An iterator that will make additions calls to API to retrieve additional
            elements if needed

        """

        return PagedGetIterator(url=self.url + path, api_key=api_key, params=params)

    @except_connection_error
    def post(self, path, api_key, data):
        """

        Parameters
        ----------
        path: str
            relative path to endpoint. Like '/user' or '/workspaces'
        api_key: str
            api key to send with request
        data: Dict
            data to send as json

        Returns
        -------
        Dict or List:
            Json-interpreted response from server

        """
        response_raw = requests.post(
            self.url + path,
            headers={"X-Api-key": api_key, "content-type": "application/json"},
            json=data
        )
        return APIRawResponse(response_raw).parse()

    @except_connection_error
    def put(self, path, api_key, data):
        """

        Parameters
        ----------
        path: str
            relative path to endpoint. Like '/user' or '/workspaces'
        api_key: str
            api key to send with request
        data: Dict
            data to send as json

        Returns
        -------
        Dict or List:
            Json-interpreted response from server

        """
        response_raw = requests.put(
            self.url + path,
            headers={"X-Api-key": api_key, "content-type": "application/json"},
            json=data
        )
        return APIRawResponse(response_raw).parse()

    @except_connection_error
    def patch(self, path, api_key, data):
        """

        Parameters
        ----------
        path: str
            relative path to endpoint. Like '/user' or '/workspaces'
        api_key: str
            api key to send with request
        data: Dict
            data to send as json

        Returns
        -------
        Dict or List:
            Json-interpreted response from server

        """
        response_raw = requests.patch(
            self.url + path,
            headers={"X-Api-key": api_key, "content-type": "application/json"},
            json=data
        )
        return APIRawResponse(response_raw).parse()


class PagedGetIterator:

    def __init__(self, url: str, api_key: str, params: Dict[str, str] = None):
        """Large responses are paged by clockify, meaning a single call will only
        return data on the first N items. To get all items, repeated calls are
        needed. This iterator returns items and repeats calls when needed until
        all items have been retrieved


        Parameters
        ----------
        url: str
            relative path to endpoint. Like '/user' or '/workspaces'
        api_key: str
            api key to send with request
        params: Dict, optional
            Request parameters to send. Defaults to empty dict

        Notes
        -----
        Assumes the API endpoint at url supports the following request parameters:
        page: integer
            the page to return
        page-size: integer
            the number of items to return on each page

        Returns
        -------
        Dict or List:
            Json-interpreted response from server
        """
        self.url = url
        self.api_key = api_key
        if not params:
            params = {}
        self.params = params
        self.current_page_iterator = iter([])
        self.current_page_number = 0
        self.page_size = 50
        self.might_have_more = True

    def get_response(self, page: int) -> List[Dict]:
        """Get responses for given page
        """
        self.params['page'] = str(page)
        self.params['page-size'] = str(self.page_size)
        response_raw = requests.get(
            self.url,
            headers={"X-Api-key": self.api_key, "content-type": "application/json"},
            params=self.params
        )
        return APIRawResponse(response_raw).parse()

    def get_next_page(self):
        """Try to call API for the next batch of results"""
        self.current_page_number += 1
        items = self.get_response(page=self.current_page_number)
        if len(items) < self.page_size:
            # less items than requested were returned. This is the last page
            self.might_have_more = False
        self.current_page_iterator = iter(items)

    def __next__(self) -> Dict:

        try:  # Return an item from the last response
            return self.current_page_iterator.__next__()
        except StopIteration:
            if self.might_have_more:
                # the last response items ran out, but there could be more. get.
                self.get_next_page()
                return self.current_page_iterator.__next__()
            else:
                # we were already at the last page. End of iteration
                raise

    def __iter__(self):
        return self


class APIRawResponse:

    def __init__(self, raw_response):
        """A response as received from an API server

        Parameters
        ----------
        raw_response: requests response
        """
        self.raw_response = raw_response

    def parse(self):
        """Return API response as dict. If the response encodes an API error, raise Exception

        Raises
        ------
        APIServer404:
            When the raw response describes an API code 404 exception
        APIServerException
            When the raw response describes any other API exception
        APIResponseParseException
            If the response cannot be parsed as JSON

        Returns
        -------
        Dict
            The parsed response

        """
        if self.raw_response.status_code in [200, 201]:
            return self.parse_json(self.raw_response)
        else:
            error_response = self.parse_json_clockify_error(self.raw_response)
            msg = f"HTTP {self.raw_response.status_code} containing API error '{self.raw_response.text}'"
            if error_response.code == 404:
                raise APIServer404(msg, error_response=error_response)
            else:
                raise APIServerException(msg, error_response=error_response)

    @staticmethod
    def parse_json(response):
        """Parse response json string from server into object

        Parameters
        ----------
        response: requests.response
            containing json encoded string received from API

        Raises
        ------
        APIResponseParseException
            When response text cannot be parsed as json

        Returns
        -------
        Dict
            Parsed json

        """
        try:
            return response.json()
        except JSONDecodeError:
            msg = f"Could not parse response as JSON: '{response.text}'"
            raise APIResponseParseException(msg)

    def parse_json_clockify_error(self, error_text):
        """Parse response json string containing an API error from server into object

        Parameters
        ----------
        error_text: str
            json encoded error string received from API

        Raises
        ------
        APIResponseParseException
            When response text cannot be parsed as json or required information is missing from response

        Returns
        -------
        APIErrorResponse
        """
        parsed = self.parse_json(error_text)
        # clockify api errors use either 'description' or 'message' for human readable component.
        if 'message' in parsed.keys():
            message = parsed['message']
        elif 'description' in parsed.keys():
            message = parsed['description']
        else:
            msg = f'Could not find "message" or "description" in {parsed}'
            raise APIResponseParseException(msg)

        if 'code' not in parsed.keys():
            msg = f'Could not find "code" in {parsed}'
            raise APIResponseParseException(msg)

        return APIErrorResponse(code=parsed['code'], message=message)


class APIErrorResponse:

    def __init__(self, code, message):
        """An error response received from the API

        Parameters
        ----------
        code: int
        message: str
        """
        self.code = code
        self.message = message


class APIException(ClockifyClientException):
    """Base exception for this module. 'Something' went wrong"""
    pass


class APIResponseParseException(APIException):
    pass


class APIServerException(APIException):
    """An exception in the API server itself, communicated properly by the API server """
    def __init__(self, *args, error_response: APIErrorResponse):
        """

        Parameters
        ----------
        args
        error_response: APIErrorResponse
            The response received from server
        """
        super().__init__(*args)
        self.error_response = error_response


class APIServer404(APIServerException):
    """API returns a message with code 404 """
    pass
