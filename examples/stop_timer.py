""" Add a time entry to a workspace
"""

from os import environ

from clockifyclient.api import APIServer
from clockifyclient.client import APISession

session = APISession(api_server=APIServer("https://api.clockify.me/api/v1"),
                     api_key=environ["API_KEY"])

stopped = session.stop_timer()

if stopped:
    print(f'stopped {stopped}. Set endtime {stopped.end}')
else:
    print('Stopped nothing. No timer was running')
