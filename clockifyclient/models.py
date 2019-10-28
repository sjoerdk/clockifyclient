""" Models the objects with which the clockify API works. One level above json dicts.
Models as simply as possible, omitting any fields not used by this package
"""
import datetime

from clockifyclient.exceptions import ClockifyClientException


class ClockifyDatetime:

    date_string_format = "%Y-%m-%dT%H:%M:%SZ"

    """For converting between python datetime and clockify datetime string"""
    def __init__(self, datetime):
        """

        Parameters
        ----------
        datetime: datetime
            set this date time
        """
        self.datetime = datetime

    @classmethod
    def init_from_string(cls, clockify_date_string):
        return cls(datetime=datetime.datetime.strptime(clockify_date_string, cls.date_string_format))

    def __str__(self):
        return datetime.datetime.strftime(self.datetime, self.date_string_format)


class APIObject:
    """An object that can be returned by the clockify API"""

    def __init__(self, obj_id):
        """

        Parameters
        ----------
        obj_id: str
            object id hash
        """
        self.obj_id = obj_id

    def __str__(self):
        return f"API object {self.obj_id}"

    @classmethod
    def get_item(cls, dict_in, key, raise_error=True):
        """ Get item from dict, raise exception or return None if not found

        Parameters
        ----------
        dict_in: Dict
            dict to search in
        key: str
            dict key
        raise_error: Bool, optional
            If True raises error when key not found. Otherwise returns None. Defaults to True

        Raises
        ------
        ObjectParseException
            When key is not found in dict and raise_error is False

        Returns
        -------
        object
            Dict item at key
        None
            If item not found and raise_error is True

        """
        try:
            return dict_in[key]
        except KeyError:
            msg = f"Could not find key '{key}' in '{dict_in}'"
            raise ObjectParseException(msg)

    @classmethod
    def get_datetime(cls, dict_in, key, raise_error=True):
        """ Try to find key in dict and parse to datetime

        Parameters
        ----------
        dict_in: Dict
            dict to search in
        key: str
            dict key
        raise_error: Bool, optional
            If True raises error when key not found. Otherwise returns None. Defaults to True

        Raises
        ------
        ObjectParseException
            When key is not found in dict (if raise_error is True) or could not be parsed to datetime.
            Exception is always raised when value cannot be parsed

        Returns
        -------
        datetime
            parsed date from dict[key]
        None
            If item not found and raise_error is True
        """
        date_str = cls.get_item(dict_in, key, raise_error=raise_error)
        if not date_str:
            return None
        try:
            return ClockifyDatetime.init_from_string(date_str).datetime
        except ValueError as e:
            msg = f"Error parsing {date_str} to datetime: '{e}'"
            raise ObjectParseException(msg)

    @classmethod
    def init_from_dict(cls, dict_in):
        """ Create an instance of this class from the expected json dict returned from Clockify API
        Parameters
        ----------
        dict_in: Dict
            As returned from Clockify API

        Raises
        ------
        ObjectParseException
            If dict_in does not contain all required field for creating an object

        Returns
        -------
        instance of this class, initialized to the values in dict_in

        """
        return cls(obj_id=cls.get_item(dict_in=dict_in, key='id'),
                   name=cls.get_item(dict_in=dict_in, key='name'))


class NamedAPIObject(APIObject):

    def __init__(self, obj_id, name):
        """

        Parameters
        ----------
        obj_id: str
            object id hash
        name: str
            human readable string
        """
        super().__init__(obj_id=obj_id)
        self.name = name

    def __str__(self):
        return f"API object '{self.name}' {self.obj_id}"

    @classmethod
    def init_from_dict(cls, dict_in):
        return cls(obj_id=cls.get_item(dict_in=dict_in, key='id'),
                   name=cls.get_item(dict_in=dict_in, key='name'))


class User(NamedAPIObject):

    def __str__(self):
        return f"User '{self.name}' ({self.obj_id})"


class Workspace(NamedAPIObject):
    def __str__(self):
        return f"Workspace '{self.name}' ({self.obj_id})"


class Project(NamedAPIObject):
    def __str__(self):
        return f"Project '{self.name}' ({self.obj_id})"


class ProjectStub(Project):
    """A project with only an id. This occurs when a project ID is returned by API as part of a different query"""
    def __init__(self, obj_id):
        super().__init__(obj_id=obj_id, name=None)

    def __str__(self):
        return f"ProjectStub ({self.obj_id})"


class TimeEntry(APIObject):

    def __init__(self, obj_id, start, description='', project=None, end=None):
        """

        Parameters
        ----------
        obj_id: str
            object id hash
        start: DateTime
            Start of time entry
        description: str, optional
            Human readable description of this time entry. Defaults to empty string
        project: Project, optional
            Project associated with this entry. Defaults to None
        end: DateTime, optional
            End of time entry. Defaults to None, meaning timer mode is activated
        """
        super().__init__(obj_id=obj_id)
        self.start = start
        self.description = description
        self.project = project
        self.end = end

    @staticmethod
    def truncate(msg, length=30):
        if msg[(length):]:
            return msg[:(length-3)] + "..."
        else:
            return msg

    def __str__(self):
        return f"TimeEntry ({self.obj_id}) - '{self.truncate(self.description)}'"

    @classmethod
    def init_from_dict(cls, dict_in):
        # required parameters
        interval = cls.get_item(dict_in, 'timeInterval')
        obj_id = cls.get_item(dict_in=dict_in, key='id')
        start = cls.get_datetime(dict_in=interval, key='start')

        # optional parameters
        description = cls.get_item(dict_in=dict_in, key='description', raise_error=False)
        project_id = cls.get_item(dict_in=dict_in, key='projectId', raise_error=False)
        if project_id:
            project = ProjectStub(obj_id=project_id)
        else:
            project = None
        end = cls.get_datetime(dict_in=interval, key='end', raise_error=False)

        return cls(obj_id=obj_id,
                   start=start,
                   description=description,
                   project=project,
                   end=end
                   )

    def to_dict(self):
        """As dict that can be sent to API"""
        as_dict = {"id": self.obj_id,
                   "start": str(ClockifyDatetime(self.start)),
                   "description": self.description
                   }
        if self.end:
            as_dict["end"] = str(ClockifyDatetime(self.end))
        if self.project:
            as_dict["projectId"] = self.project.obj_id

        return {x: y for x, y in as_dict.items() if y}  # remove items with None value


class ObjectParseException(ClockifyClientException):
    pass
