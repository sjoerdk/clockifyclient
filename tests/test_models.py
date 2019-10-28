#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import json

from clockifyclient.models import TimeEntry, User, Project, Workspace, APIObject, ProjectStub, NamedAPIObject, \
    ClockifyDatetime
from tests.factories import ClockifyMockResponses


def test_time_entry_from_dict():
    time_entry_dict = json.loads(ClockifyMockResponses.POST_TIME_ENTRY.text)
    time_entry = TimeEntry.init_from_dict(time_entry_dict)
    assert time_entry.description == 'testing description'

    time_entry_dict_again = TimeEntry.to_dict(time_entry)
    assert time_entry_dict_again['start'] == '2019-10-23T17:18:58Z'
    assert time_entry_dict_again['description'] == 'testing description'
    assert time_entry_dict_again['projectId'] == '123456'


def test_time_entry(a_date):
    """Test with different input parameters"""
    # minimal parameters
    entry = TimeEntry(obj_id=None,
                      start=a_date,
                      description='test description')
    entry.to_dict()


def test_date_conversion():
    example_string = "2018-06-12T14:01:41Z"
    datetime = ClockifyDatetime.init_from_string(example_string).datetime
    assert datetime.year == 2018
    assert datetime.month == 6
    assert datetime.day == 12
    assert datetime.hour == 14
    assert datetime.minute == 1

    assert str(ClockifyDatetime(datetime)) == example_string

    cltime = ClockifyDatetime(datetime)
    ClockifyDatetime.init_from_string(str(cltime))


def test_str(a_date):
    """Getting coverage up """
    str(User(obj_id='123', name='test'))
    str(Project(obj_id='123', name='test'))
    str(ProjectStub(obj_id='123'))
    str(Workspace(obj_id='123', name='test'))
    str(APIObject(obj_id='123'))
    str(NamedAPIObject(obj_id='123', name='test'))

    str(TimeEntry(obj_id='123', start=a_date))


def test_truncate(a_date):
    entry = TimeEntry(obj_id='123', start=a_date)
    assert str(entry). endswith("''")
    entry.description = 'A short description'
    assert str(entry).endswith("description'")
    entry.description = 'A longer description thats 30c'
    assert str(entry).endswith("thats 30c'")
    entry.description = 'A longer description thats a lot longer then 30 characters'
    assert str(entry).endswith("thats ...'")
