"""Add a time entry to a workspace, start timer, and associate with a project"""

from os import environ

from clockifyclient.api import APIServer
from clockifyclient.client import APISession

session = APISession(
    api_server=APIServer("https://api.clockify.me/api/v1"), api_key=environ["API_KEY"]
)

if session.get_projects():
    project = session.get_projects()[
        0
    ]  # For this example, just get the first project you find
else:
    project = None  # Or, if there are no projects, just don't use a project

response = session.add_time_entry(
    start_time=session.now(), description="A test time entry", project=project
)

print(f"Created {response}")
