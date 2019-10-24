#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import json

from clockifyclient.models import TimeEntry, User, Project, Workspace, APIObject, ProjectStub, NamedAPIObject
from tests.factories import ClockifyMockResponses


def test_time_entry_from_dict():
    time_entry_dict = json.loads(ClockifyMockResponses.POST_TIME_ENTRY.text)
    time_entry = TimeEntry.init_from_dict(time_entry_dict)
    assert time_entry.description == 'testing description'

    time_entry_dict_again = TimeEntry.to_dict(time_entry)
    assert time_entry_dict_again['start'] == '2019-10-23T17:18:58Z'
    assert time_entry_dict_again['description'] == 'testing description'
    assert time_entry_dict_again['projectId'] == '123456'


def test_date_conversion():
    example_string = "2018-06-12T14:01:41Z"
    datetime = TimeEntry.to_datetime(example_string)
    assert datetime.year == 2018
    assert datetime.month == 6
    assert datetime.day == 12
    assert datetime.hour == 14
    assert datetime.minute == 1

    assert TimeEntry.to_date_string(datetime_in=datetime) == example_string


def test_str():
    """Getting coverage up """
    str(User(obj_id='123', name='test'))
    str(Project(obj_id='123', name='test'))
    str(ProjectStub(obj_id='123'))
    str(Workspace(obj_id='123', name='test'))
    str(APIObject(obj_id='123'))
    str(NamedAPIObject(obj_id='123', name='test'))

    str(TimeEntry(obj_id='123', start=datetime.datetime(year=2000, month=1, day=1)))


