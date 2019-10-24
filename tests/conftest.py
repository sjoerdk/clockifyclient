"""Conftest.py is loaded for each pytest. Contains fixtures shared by multiple tests, amongs other things """
from tests.factories import RequestsMock
from pytest import fixture


@fixture
def mock_requests(monkeypatch):
    """Make sure the api module does not do any actual http calls. Also makes it possible to set http responses

    Returns
    -------
    RequestsMock
    """
    requests_mock = RequestsMock()
    monkeypatch.setattr("clockifyclient.api.requests", requests_mock.requests)
    return requests_mock

