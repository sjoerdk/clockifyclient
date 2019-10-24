#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime

import pytest

from clockifyclient.api import APIServer, APIServerException
from clockifyclient.client import ClockifyAPI
from clockifyclient.models import TimeEntry, ProjectStub, Project, Workspace
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
def an_api(a_server):
    return ClockifyAPI(api_server=a_server)


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


def test_api_add_time_entry(mock_requests, an_api, a_workspace, a_project):
    mock_requests.set_response(ClockifyMockResponses.POST_TIME_ENTRY)
    a_time_entry = TimeEntry(obj_id=None,
                             start=datetime.datetime(year=2019, month=10, day=12, hour=14, minute=10, second=1),
                             description='test description',
                             project=a_project)

    # should not raise exceptions. Not much else to check with these mocks
    an_api.add_time_entry(api_key='mock_key', workspace=a_workspace, time_entry=a_time_entry)

