"""Models the clockify API. Tries to stay close to the actual endpoints.
This layer is the only one that should do actual http queries
"""
import requests

from clockifyclient.exceptions import ClockifyClientException


class APIServer:
    """Models a clockify API server. Basic HTTP interaction. Returns json and raises exceptions
    """

    def __init__(self, url):
        """

        Parameters
        ----------
        url: str
            url of the api
        """
        self.url = url

    def get(self, path, api_key):
        """

        Parameters
        ----------
        path: str
            relative path to endpoint. Like '/user' or '/workspaces'
        api_key: str
            api key to send with request

        Returns
        -------
        Dict or List:
            Json-interpreted response from server

        """
        response_raw = requests.get(
            self.url + path,
            headers={"X-Api-key": api_key, "content-type": "application/json"},
        )
        self.interpret_raw_response(response_raw)
        return response_raw.json()

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
        self.interpret_raw_response(response_raw)
        return response_raw.json()

    @staticmethod
    def interpret_raw_response(response):
        """Check HTTP response and throw helpful python exception if needed.

        Will raise errors for any response code other than 200(OK) or 201(Created)

        Parameters
        ----------
        response: :obj:`requests.models.Response`
            A response such as it is returned by the python requests library

        Returns
        -------
            Nothing

        Raises
        ------
        APIServerException:
            When anything goes wrong
        """

        if response.status_code == 200 or response.status_code == 201:
            # response succeeded, no further checking needed
            return

        else:
            msg = f"HTTP error {response.status_code}. Server returned error: '{response.text}' " \
                  f"when calling {response.url}"
            raise APIServerException(msg)


class APIException(ClockifyClientException):
    """Base exception for this module. 'Something' went wrong"""
    pass


class APIServerException(APIException):
    """An exception communicated by the API server """
    pass
