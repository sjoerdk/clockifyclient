import requests

from clockifyclient.exceptions import ClockifyClientException


def except_connection_error(func):
    """decorator to translate any requests connectionerror to APIException.

    Made this to have all common exceptions derive from ClockifyClientException
    """

    def decorated(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except requests.exceptions.ConnectionError as e:
            raise ClockifyClientException(f'Requests connection error: {e}')

    return decorated
