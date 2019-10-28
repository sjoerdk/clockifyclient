#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
from unittest.mock import Mock

import pytest

from clockifyclient.api import APIServer, APIServerException, APIErrorResponse
from clockifyclient.client import ClockifyAPI, APISession
from clockifyclient.models import TimeEntry, ProjectStub, Project, Workspace, User
from tests.factories import ClockifyMockResponses


@pytest.fixture()
def a_server():
    return APIServer("localhost")


@pytest.fixture()
def a_project():
    return Project(obj_id='1234', name='testproject')


@pytest.fixture()
def a_workspace():
    return Workspace(obj_id='123235', name='testworkspace')


@pytest.fixture()
def a_user():
    return User(obj_id='1232356', name='testuser')


@pytest.fixture()
def an_api(a_server):
    return ClockifyAPI(api_server=a_server)


@pytest.fixture()
def a_time_entry(a_project):
    return TimeEntry(obj_id=None,
                     start=datetime.datetime(year=2019, month=10, day=12, hour=14, minute=10, second=1),
                     description='test description',
                     project=a_project)


@pytest.fixture()
def a_mock_api(mock_requests, an_api, a_project, a_user, a_workspace, a_time_entry):
    """A ClockifyAPI that just returns default objects for all methods, not calling any server

    """

    mock_api = Mock(spec=ClockifyAPI)
    mock_api.get_projects.return_value = [a_project]
    mock_api.get_user.return_value = a_user
    mock_api.get_workspaces.return_value = [a_workspace]
    mock_api.add_time_entry.return_value = a_time_entry
    mock_api.set_active_time_entry_end.return_value = a_time_entry
    return mock_api


def test_api_calls_get(mock_requests, an_api):
    """Some regular calls to api should yield correct python objects """
    mock_requests.set_response(ClockifyMockResponses.GET_WORKSPACES)
    workspaces = an_api.get_workspaces(api_key='mock_key')
    assert len(workspaces) == 1
    assert workspaces[0].obj_id == '12345'
    assert workspaces[0].name == 'testuser'

    mock_requests.set_response(ClockifyMockResponses.GET_USER)
    user = an_api.get_user(api_key='mock_key')
    assert user.obj_id == '1234'
    assert user.name == 'testuser'

    mock_requests.set_response(ClockifyMockResponses.GET_PROJECTS)
    projects = an_api.get_projects(api_key='mock_key', workspace=workspaces[0])
    assert len(projects) == 2
    assert projects[0].name == 'Project1'
    assert projects[1].obj_id == '234567'


def test_api_add_time_entry(mock_requests, an_api, a_workspace, a_time_entry):
    mock_requests.set_response(ClockifyMockResponses.POST_TIME_ENTRY)

    # should not raise exceptions. Not much else to check with these mocks
    an_api.add_time_entry(api_key='mock_key', workspace=a_workspace, time_entry=a_time_entry)


def test_set_active_time_entry_end(mock_requests, an_api, a_workspace, a_user, a_date):
    mock_requests.set_response(ClockifyMockResponses.POST_TIME_ENTRY)
    response = an_api.set_active_time_entry_end(api_key='test', workspace=a_workspace, user=a_user, end_time=a_date)
    assert response is not None

    # if there is no currently running entry
    mock_requests.set_response(ClockifyMockResponses.CURRENTLY_RUNNING_ENTRY_NOT_FOUND)
    response = an_api.set_active_time_entry_end(api_key='test', workspace=a_workspace, user=a_user, end_time=a_date)
    assert response is None


def test_session(mock_requests, a_mock_api):
    """Run some session commands with a mocked underlying API"""
    session = APISession(api_server=an_api, api_key='test')
    session.api = a_mock_api
    session.add_time_entry(start_time=None, description='test', project=None)
    session.stop_timer()


def test_session_exception(mock_requests, a_mock_api):
    session = APISession(api_server=an_api, api_key='test')
    session.api = a_mock_api
    session.api.get_workspaces.side_effect = APIServerException('Something went wrong with the API',
                                                          error_response=APIErrorResponse(code=999,
                                                                                          message='mock error'))
    with pytest.raises(APIServerException):
        session.add_time_entry(start_time=None, description='test', project=None)
