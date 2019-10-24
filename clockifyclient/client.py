# -*- coding: utf-8 -*-
from clockifyclient.api import APIServer
from clockifyclient.models import Workspace, User, Project, TimeEntry


class APISession:
    """Models the interaction of one user with one workspace. Caches current user and workspace

    Made this to make interaction quicker and make sure you only have to input an API key once
    """

    pass


class ClockifyAPI:
    """A Clockify API in the python world. Returns python objects. Does not know about http requests

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
        response = self.api_server.get(path='/workspaces', api_key=api_key)
        return [Workspace.init_from_dict(x) for x in response]

    def get_user(self, api_key):
        """Get the user for the given api key

        Parameters
        ----------
        api_key: str
            Clockify Api key

        Returns
        -------
        User

        """
        response = self.api_server.get(path='/user', api_key=api_key)
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
        response = self.api_server.get(path=f'/workspaces/{workspace.obj_id}/projects', api_key=api_key)
        return [Project.init_from_dict(x) for x in response]

    def add_time_entry(self, api_key: str, workspace: Workspace, time_entry: TimeEntry):
        """

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

        result = self.api_server.post(path=f"/workspaces/{workspace.obj_id}/time-entries",
                                      api_key=api_key,
                                      data=time_entry.to_dict())

        return TimeEntry.init_from_dict(result)