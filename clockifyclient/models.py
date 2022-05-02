"""Models the objects with which the clockify API works. One level above json dicts.
Models as simply as possible, omitting any fields not used by this package
"""
import dateutil
import dateutil.parser as date_parser

from clockifyclient.exceptions import ClockifyClientException


class ClockifyDatetime:
    """For converting between python datetime and clockify datetime string

    ClockifyDatetime is always timezone aware. If initialized with a naive datetime,
    local time is assumed
    """

    clockify_datetime_format = "%Y-%m-%dT%H:%M:%SZ"

    def __init__(self, datetime_in):
        """Create

        Parameters
        ----------
        datetime_in: datetime
            Set this date time. If no timezone is set, will assume local timezone
        """
        if not datetime_in.tzinfo:
            datetime_in = datetime_in.replace(tzinfo=dateutil.tz.tzlocal())
        self.datetime = datetime_in

    @property
    def datetime_utc(self):
        """Datetime in the UTC time zone"""
        return self.datetime.astimezone(dateutil.tz.UTC)

    @property
    def datetime_local(self):
        """Datetime as local time"""
        return self.datetime.astimezone(dateutil.tz.tzlocal())

    @property
    def clockify_datetime(self):
        """Datetime a clockify-format string"""
        return self.datetime_utc.strftime(self.clockify_datetime_format)

    @classmethod
    def init_from_string(cls, clockify_date_string):
        return cls(date_parser.parse(clockify_date_string))

    def __str__(self):
        return self.clockify_datetime


# for indicating a value is not set while allowing None to be a valid value
NOT_SET = object()


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
    def get_item(cls, dict_in, key, default=NOT_SET):
        """Get item from dict, raise exception or return default if not found

        Parameters
        ----------
        dict_in: Dict
            dict to search in
        key: str
            dict key
        default: any, optional
            return this when key is not found. Default is to raise exception instead

        Raises
        ------
        ObjectParseException
            When key is not found in dict and no default is set

        Returns
        -------
        any
            Dict item at key or default

        """
        try:
            return dict_in[key]
        except KeyError as e:
            if default == NOT_SET:
                msg = f"Could not find key '{key}' in '{dict_in}'"
                raise ObjectParseException(msg) from e
            else:
                return default

    @classmethod
    def get_datetime(cls, dict_in, key, default=NOT_SET):
        """Try to find key in dict and parse to datetime

        Parameters
        ----------
        dict_in: Dict
            dict to search in
        key: str
            dict key
        default: any, optional
            Return this when key is not found in dict. Defaults to raising exception

        Raises
        ------
        ObjectParseException
            When key is not found in dict  or could not be parsed to datetime.
            Exception is always raised when value cannot be parsed

        Returns
        -------
        datetime
            parsed date from dict[key]
        any
            If item not found and default is set
        """
        date_str = cls.get_item(dict_in, key, default=default)
        if not date_str:
            if default == NOT_SET:
                raise ObjectParseException(f"Key {key} not found")
            else:
                return default
        try:
            return ClockifyDatetime.init_from_string(date_str).datetime
        except ValueError as e:
            msg = f"Error parsing {date_str} to datetime: '{e}'"
            raise ObjectParseException(msg) from e

    @classmethod
    def init_from_dict(cls, dict_in):
        """Create an instance of this class from the expected json dict returned
        from Clockify API

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
        return cls(obj_id=cls.get_item(dict_in=dict_in, key="id"),)


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
        return cls(
            obj_id=cls.get_item(dict_in=dict_in, key="id"),
            name=cls.get_item(dict_in=dict_in, key="name"),
        )


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
    """A project with only an id. This occurs when a project ID is returned by
    API as part of a different query
    """

    def __init__(self, obj_id):
        super().__init__(obj_id=obj_id, name=None)

    def __str__(self):
        return f"ProjectStub ({self.obj_id})"


class Task(NamedAPIObject):
    def __str__(self):
        return f"Task '{self.name}' ({self.obj_id})"


class TaskStub(Task):
    """A task with only an id. This occurs when a task ID is returned by
    API as part of a different query
    """

    def __init__(self, obj_id):
        super().__init__(obj_id=obj_id, name=None)

    def __str__(self):
        return f"TaskStub ({self.obj_id})"


class TimeEntry(APIObject):
    def __init__(
        self, obj_id, start, description="", project=None, task=None, end=None
    ):
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
        task: Task, optional
            Task associated with this entry. Defaults to None
        end: DateTime, optional
            End of time entry. Defaults to None, meaning timer mode is activated
        """
        super().__init__(obj_id=obj_id)
        self.start = start
        self.description = description
        self.project = project
        self.task = task
        self.end = end

    @staticmethod
    def truncate(msg, length=30):
        if msg[(length):]:
            return msg[: (length - 3)] + "..."
        else:
            return msg

    def __str__(self):
        return f"TimeEntry ({self.obj_id}) - '{self.truncate(self.description)}'"

    @classmethod
    def init_from_dict(cls, dict_in):
        # required parameters
        interval = cls.get_item(dict_in, "timeInterval")
        obj_id = cls.get_item(dict_in=dict_in, key="id")
        start = cls.get_datetime(dict_in=interval, key="start")

        # optional parameters
        description = cls.get_item(dict_in=dict_in, key="description")
        project_id = cls.get_item(dict_in=dict_in, key="projectId", default=None)
        if project_id:
            project = ProjectStub(obj_id=project_id)
        else:
            project = None
        end = cls.get_datetime(dict_in=interval, key="end", default=None)

        task_id = cls.get_item(dict_in=dict_in, key="taskId", default=None)
        if task_id:
            task = TaskStub(obj_id=task_id)
        else:
            task = None
        end = cls.get_datetime(dict_in=interval, key="end", default=None)

        return cls(
            obj_id=obj_id,
            start=start,
            description=description,
            project=project,
            task=task,
            end=end,
        )

    def to_dict(self):
        """As dict that can be sent to API"""
        as_dict = {
            "id": self.obj_id,
            "start": str(ClockifyDatetime(self.start)),
            "description": self.description,
        }
        if self.end:
            as_dict["end"] = str(ClockifyDatetime(self.end))
        if self.project:
            as_dict["projectId"] = self.project.obj_id
        if self.task:
            as_dict["taskId"] = self.task.obj_id

        return {x: y for x, y in as_dict.items() if y}  # remove items with None value


class TimeEntryQuery:
    """A query for the time-entries endpoint"""

    def __init__(self, description: str):
        """

        Parameters
        ----------
        description: str
            time entries will be filtered by description.

        """
        self.description = description

    def __str__(self):
        return f"TimeEntryQuery ('{self.to_dict()}'"

    def to_dict(self):
        """As dict that can be sent to API"""
        as_dict = {"description": self.description}
        return {x: y for x, y in as_dict.items() if y}  # remove items with None value


class ObjectParseException(ClockifyClientException):
    pass
