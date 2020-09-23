"""Editing time entries"""
from os import environ

from clockifyclient.api import APIServer
from clockifyclient.client import APISession
from clockifyclient.models import TimeEntryQuery

session = APISession(
    api_server=APIServer("https://api.clockify.me/api/v1"), api_key=environ["API_KEY"]
)

projects = {x.name: x for x in session.get_projects()}

# get entries from clockify
entries = session.get_time_entries(
    query=TimeEntryQuery(description="emails"), limit=None
)

# Prune away unwanted results
print(f"{len(entries)} entries found")
in_entries = [x for x in entries if x.project is None]

# change project for all those
for entry in in_entries:
    entry.project = projects["Research Bureau"]

print(f"saving {len(in_entries)} entries..")
session.add_time_entries(in_entries)
print("Done")
