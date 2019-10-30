#!/usr/bin/env python
# -*- coding: utf-8 -*-
import json

import dateutil
import pytest

from clockifyclient.models import TimeEntry, User, Project, Workspace, APIObject, ProjectStub, NamedAPIObject, \
    ClockifyDatetime
from tests.factories import ClockifyMockResponses


@pytest.fixture()
def mock_models_timezone(monkeypatch):
    """Set timezone to +8/+8"""
    monkeypatch.setattr('clockifyclient.models.dateutil.tz.tzlocal', lambda: dateutil.tz.gettz('Asia/Irkutsk'))


def test_time_entry_from_dict(mock_models_timezone):
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


def test_date_conversion(mock_models_timezone):
    example_string = "2018-06-12T14:01:41+00:00"
    datetime = ClockifyDatetime.init_from_string(example_string).datetime_utc
    assert datetime.year == 2018
    assert datetime.month == 6
    assert datetime.day == 12
    assert datetime.hour == 14
    assert datetime.minute == 1

    # str representation should always be UTC in Clockify format, ending in Z (for UTC)
    assert str(ClockifyDatetime(datetime)) == "2018-06-12T14:01:41Z"
    # Naive datetime should have been branded with local (mock +8)
    assert str(ClockifyDatetime.init_from_string("2018-06-12T14:01:41")) == "2018-06-12T06:01:41Z"

    # naive datetime, should be branded as local timezone, so the mock +8 timezone should have been subtracted for utc
    assert ClockifyDatetime.init_from_string("2018-06-12T14:01:41").datetime_utc.hour == 6
    # but the normal datetime should be unaffected: should be as input
    assert ClockifyDatetime.init_from_string("2018-06-12T14:01:41").datetime.hour == 14

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
