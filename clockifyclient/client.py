# -*- coding: utf-8 -*-
import datetime
from itertools import islice
from typing import Generator, List, Optional

from clockifyclient.api import APIServer, APIServer404
from clockifyclient.models import (
    Task,
    TimeEntryQuery,
    Workspace,
    User,
    Project,
    TimeEntry,
    ClockifyDatetime,
)
from functools import lru_cache


class APISession:
    """Models the interaction of one user with one workspace. Caches current user,
    workspace and projects.

    To make basic interactions quicker this class makes two simplifying assumptions:
    * All actions pertain to one user, the owner of the api_key
    * All actions pertain to only one workspace, the user's default workspace

    """

    def __init__(self, api_server: APIServer, api_key: str):
        """
        Parameters
        ----------
        api_server: APIServer
            Server to use for communication
        api_key: str
            Clockify Api key
        """
        self.api_key = api_key
        self.api = ClockifyAPI(api_server=api_server)

    @lru_cache()
    def get_default_workspace(self):
        return self.api.get_workspaces(api_key=self.api_key)[0]

    @lru_cache()
    def get_user(self):
        return self.api.get_user(api_key=self.api_key)

    @lru_cache()
    def get_projects(self):
        return self.api.get_projects(
            api_key=self.api_key, workspace=self.get_default_workspace()
        )

    @lru_cache()
    def get_tasks(self, project: Project):
        return self.api.get_tasks(
            api_key=self.api_key,
            workspace=self.get_default_workspace(),
            project=project,
        )

    def add_time_entries(self, entries: List[TimeEntry]):
        for entry in entries:
            self.add_time_entry_object(entry)

    def add_time_entry_object(self, time_entry: TimeEntry):
        """Add the given time entry to the default workspace

        Parameters
        ----------
        time_entry: TimeEntry
            The time entry to add

        Returns
        -------
        TimeEntry
            The created time entry

        """
        return self.api.add_time_entry_object(
            api_key=self.api_key,
            workspace=self.get_default_workspace(),
            time_entry=time_entry,
        )

    def add_time_entry(self, start_time, end_time=None, description=None, project=None):
        """Add a time entry to default workspace. If no end time is given stopwatch
         mode is activated.

        This will stop any previously running stopwatch

        Parameters
        ----------
        start_time: datetime, UTC
            Set start of time entry to this
        end_time: datetime, UTC, optional
            Set end of time entry to this. If not given, activate stopwatch mode.
            Defaults to None
        description: str, optional
            Description of this time entry. Defaults to None
        project: Project, optional
            Set the project that this time entry belongs to. Defaults to None

        Returns
        -------
        TimeEntry
            The created time entry

        """
        time_entry = TimeEntry(
            obj_id=None,
            start=start_time,
            description=description,
            project=project,
            end=end_time,
        )

        return self.add_time_entry_object(time_entry=time_entry)

    def stop_timer(self, stop_time=None):
        """Halt the current timer

        Parameters
        ----------
        stop_time: datetime, UTC, optional
            Set the end date of the timed entry to this. Defaults to None, meaning
            time will be set to utcnow()

        Returns
        -------
        TimeEntry:
            The entry that was stopped
        None:
            When there was no timer running

        """
        if not stop_time:
            stop_time = self.now()

        return self.api.set_active_time_entry_end(
            api_key=self.api_key,
            workspace=self.get_default_workspace(),
            user=self.get_user(),
            end_time=stop_time,
        )

    def get_time_entries(
        self, query: TimeEntryQuery, limit: Optional[int]
    ) -> List[TimeEntry]:
        """

        Parameters
        ----------
        query: TimeEntryQuery
            get TimeEntry objects corresponding to this query
        limit: Optional[int]
            retrieve at most this number of items. Limits calls to the server.
            Defaults to retrieving all items

        Returns
        -------
        List[TimeEntry]
            All time entries obtained from server, up to limit

        """
        return self.api.get_time_entries(
            api_key=self.api_key,
            workspace=self.get_default_workspace(),
            user=self.get_user(),
            query=query,
            limit=limit,
        )

    @staticmethod
    def now():
        """

        Returns
        -------
        datetime.datetime
        """
        return datetime.datetime.utcnow()


class ClockifyAPI:
    """A Clockify API in the python world. Returns python objects. Does not know
    about http requests

    Notes
    -----
    For lower level (http) interactions, see api.APIServer
    """

    def __init__(self, api_server: APIServer):
        """

        Parameters
        ----------
        api_server: APIServer
            Server to use for communication
        """
        self.api_server = api_server

    def get_workspaces(self, api_key):
        """Get all workspaces for the given api key

        Parameters
        ----------
        api_key: str
            Clockify Api key

        Returns
        -------
        List[Workspace]

        """
        response = self.api_server.get(path="/workspaces", api_key=api_key)
        return [Workspace.init_from_dict(x) for x in response]

    def get_user(self, api_key) -> User:
        """Get the user for the given api key

        Parameters
        ----------
        api_key: str
            Clockify Api key

        Returns
        -------
        User

        """
        response = self.api_server.get(path="/user", api_key=api_key)
        return User.init_from_dict(response)

    def get_projects(self, api_key, workspace):
        """Get all projects for given workspace

        Parameters
        ----------
        api_key: str
            Clockify Api key
        workspace: Workspace
            Get projects in this workspace

        Returns
        -------
        List[Project]

        """
        response = self.api_server.get(
            path=f"/workspaces/{workspace.obj_id}/projects", api_key=api_key
        )
        return [Project.init_from_dict(x) for x in response]

    def get_tasks(self, api_key: str, workspace: Workspace, project: Project):
        """Get all tasks for given workspace and project

        Parameters
        ----------
        api_key: str
            Clockify Api key
        workspace: Workspace
            Get projects in this workspace
        project: Project
            Project to retrieve tasks from

        Returns
        -------
        List[Task]

        """
        response = self.api_server.get(
            path=f"/workspaces/{workspace.obj_id}/projects/{project.obj_id}/tasks",
            api_key=api_key,
        )
        return [Task.init_from_dict(x) for x in response]

    def add_time_entry_object(
        self, api_key: str, workspace: Workspace, time_entry: TimeEntry
    ):
        """Save the given TimeEntry instance to server. If TimeEntry.obj_id is set
        will update existing. If TimeEntry.obj_id is None will add instance as new

        Parameters
        ----------
        api_key: str
            Clockify Api key
        workspace: Workspace
            Get projects in this workspace
        time_entry: TimeEntry
            The time entry to add

        Returns
        -------
        TimeEntry
            The created time entry

        """
        if time_entry.obj_id:
            self.api_server.put(
                path=f"/workspaces/{workspace.obj_id}/time-entries/"
                f"{time_entry.obj_id}",
                api_key=api_key,
                data=time_entry.to_dict(),
            )
            return time_entry
        else:
            result = self.api_server.post(
                path=f"/workspaces/{workspace.obj_id}/time-entries",
                api_key=api_key,
                data=time_entry.to_dict(),
            )
            return TimeEntry.init_from_dict(result)

    def get_time_entries(
        self,
        api_key: str,
        workspace: Workspace,
        user: User,
        query: TimeEntryQuery,
        limit: Optional[int] = None,
    ) -> List[TimeEntry]:
        """Get all time entries corresponding to search criteria

        Parameters
        ----------
        api_key: str
            Clockify Api key
        workspace: Workspace
            Get projects in this workspace
        user: User
            User for time entries
        query: TimeEntryQuery:
            filter time entries with this query
        limit: Optional[int]
            Retrieve this number of items maximum, potentially calling
            the server less. Defaults to None which means
            all items are retrieved.

        Notes
        -----
        This method might make multiple calls to the API if the number of results
        is over 50
        """
        return list(
            islice(
                self.get_time_entries_iterator(api_key, workspace, user, query), limit
            )
        )

    def get_time_entries_iterator(
        self, api_key: str, workspace: Workspace, user: User, query: TimeEntryQuery
    ) -> Generator[TimeEntry, None, None]:
        """Get all time entries corresponding to search criteria

        Notes
        -----
        This method might make multiple calls to the API if the number of results
        is over 50
        """
        iterator = self.api_server.get_iterator(
            path=f"/workspaces/{workspace.obj_id}/user/{user.obj_id}/time-entries",
            api_key=api_key,
            params=query.to_dict(),
        )

        return (TimeEntry.init_from_dict(x) for x in iterator)

    def set_active_time_entry_end(
        self, api_key: str, workspace: Workspace, user: User, end_time: datetime
    ):
        """Set the end time for the currently active entry

        Parameters
        ----------
        api_key: str
            Clockify Api key
        workspace: Workspace
            Get projects in this workspace
        user: User
            The use for which to end the active time entry
        end_time: datetime
            Set the end time to this

        Returns
        -------
        TimeEntry
            The updated time entry, if an active one was found
        None
            If there was no active time entry (if a stopwatch was not running)

        """
        try:
            result = self.api_server.patch(
                path=f"/workspaces/{workspace.obj_id}/user/{user.obj_id}/time-entries/",
                api_key=api_key,
                data={"end": str(ClockifyDatetime(end_time))},
            )
        except APIServer404:
            return None

        return TimeEntry.init_from_dict(result)
