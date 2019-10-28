""" Shared classes used in other tests. For generating test data """
from itertools import cycle
from typing import List
from unittest.mock import Mock
from requests.models import Response


class RequestMockResponse:
    """A description of a http server response
    """

    def __init__(self, text, response_code):
        """

        Parameters
        ----------
        text: str
            Text of this response
        response_code: int
            https response code, like 200 or 404
        """

        self.text = text
        self.response_code = response_code


class RequestsMock:
    """ Can be put in place of the requests module. Can be set to return requests.models.Response objects

    """

    def __init__(self):
        self.requests = Mock()  # for keeping track of past requests
        self.http_methods = [self.requests.get,
                             self.requests.post,
                             self.requests.patch,
                             self.requests.update]

    def set_response(self, response: RequestMockResponse):
        """Just for convenience"""
        self.set_responses([response])

    def set_responses(self, responses: List[RequestMockResponse]):
        """Any call to a http method will yield the given response. A list of responses will be looped over
        indefinitely

        Parameters
        ----------
        responses: List[RequestMockResponse]
            List of responses. Will be returned
        """

        objects = [
            self.create_response_object(response.response_code, response.text)
            for response in responses
        ]

        for method in self.http_methods:
            method.side_effect = cycle(objects)

    def set_response_exception(self, exception):
        """Any call to a http method will yield the given exception instance
        """
        for method in self.http_methods:
            method.side_effect = exception

    @staticmethod
    def create_response_object(status_code, text):
        response = Response()
        response.encoding = "utf-8"
        response.status_code = status_code
        response._content = bytes(text, response.encoding)
        response.url = "mock_url"
        return response

    def get(self, *args, **kwargs):
        return self.requests.get(*args, **kwargs)

    def post(self, *args, **kwargs):
        return self.requests.post(*args, **kwargs)

    def reset(self):
        self.requests.reset_mock()

    def called(self):
        """True if any http method was called"""
        return any([x.called for x in self.http_methods])


class ClockifyMockResponses:
    """Some cached examples of http responses from Clockify API v1. These partly come from https://clockify.me/developers-api
    and party were recorded by interacting with the server live around november 2019
    """

    # with non-existent API or missing key
    AUTH_ERROR = RequestMockResponse(
        '{"description":"Full authentication is required to access this resource","code":1000}',
        401,
    )

    # Trying to set something on
    CURRENTLY_RUNNING_ENTRY_NOT_FOUND = RequestMockResponse(
        """{"message":"Currently running time entry doesn't exist on workspace 123456 for user 123456.","code":404}""",
        404
    )

    # calling get /workspaces
    GET_WORKSPACES = RequestMockResponse(
        """[{"id": "12345", "name": "testuser", "hourlyRate": {"amount": 0, "currency": "USD"},           
             "memberships": [
              {"userId": "112424", "hourlyRate": null, "targetId": "123456",
               "membershipType": "WORKSPACE", "membershipStatus": "ACTIVE"}],
               "workspaceSettings": {"timeRoundingInReports": false, "onlyAdminsSeeBillableRates": true,
                                     "onlyAdminsCreateProject": true, "onlyAdminsSeeDashboard": false,
                                     "defaultBillableProjects": true, "lockTimeEntries": null,
                                     "round": {"round": "Round to nearest", "minutes": "15"}, "projectFavorites": true,
                                     "canSeeTimeSheet": false, "projectPickerSpecialFilter": false, "forceProjects": false,
                                     "forceTasks": false, "forceTags": false, "forceDescription": false,
                                     "onlyAdminsSeeAllTimeEntries": false, "onlyAdminsSeePublicProjectsEntries": false,
                                     "trackTimeDownToSecond": true, "projectGroupingLabel": "client", "adminOnlyPages": [],
                                     "automaticLock": null, "onlyAdminsCreateTag": false}, "imageUrl": "",
                                     "featureSubscriptionType": null}
            ]""",
        200
    )

    # calling get /user
    GET_USER = RequestMockResponse(
        """{"id":"1234","email":"test@localhost.com","name":"testuser","memberships":[{"userId":"123456",
        "hourlyRate":null,"targetId":"123456","membershipType":"WORKSPACE","membershipStatus":"ACTIVE"},
        {"userId":"24763567","hourlyRate":null,"targetId":"5645645","membershipType":"PROJECT",
        "membershipStatus":"ACTIVE"}],"profilePicture":"https://localhost/clockify/no-user-image.png",
        "activeWorkspace":"123245","defaultWorkspace":"2352346","settings":{"weekStart":"MONDAY",
        "timeZone":"Europe/Amsterdam","timeFormat":"HOUR12","dateFormat":"MM/DD/YYYY","sendNewsletter":true,
        "weeklyUpdates":false,"longRunning":false,"summaryReportSettings":{"group":"Project","subgroup":"Time Entry"},
        "isCompactViewOn":false,"dashboardSelection":"ME","dashboardViewType":"PROJECT",
        "dashboardPinToTop":false,"projectListCollapse":null,"collapseAllProjectLists":false,
        "groupSimilarEntriesDisabled":false,"myStartOfDay":"09:00","timeTrackingManual":false},"status":"ACTIVE"}""",
        200
    )

    # calling /workspaces/<workspace id>/projects
    GET_PROJECTS = RequestMockResponse(
        """[{"id":"123456","name":"Project1","hourlyRate":{"amount":0,"currency":"USD"},"clientId":"",
        "workspaceId":"123456","billable":true,"memberships":[{"userId":"123456","hourlyRate":null,"targetId":"123456",
        "membershipType":"PROJECT","membershipStatus":"ACTIVE"}],"color":"#F44336","estimate":{"estimate":"PT0S",
        "type":"AUTO"},"archived":false,"duration":"PT86H40M13S","clientName":"","public":false},{"id":"234567",
        "name":"Project2","hourlyRate":{"amount":0,"currency":"USD"},"clientId":"","workspaceId":"123456",
        "billable":true,"memberships":[{"userId":"123456","hourlyRate":null,"targetId":"123456",
        "membershipType":"PROJECT","membershipStatus":"ACTIVE"}],"color":"#E91E63","estimate":{"estimate":"PT0S",
        "type":"AUTO"},"archived":false,"duration":"PT21H7M48S","clientName":"","public":false}]""",
        200

    )

    # calling post '/workspaces/<workspace id>/time-entries'
    POST_TIME_ENTRY = RequestMockResponse(
     """{"id": "123456", "description": "testing description", "tagIds": null,
     "userId": "123456", "billable": false, "taskId": null, "projectId": "123456",
     "timeInterval": {"start": "2019-10-23T17:18:58Z", "end": null, "duration": null},
     "workspaceId": "123456", "isLocked": false}
     """, 201
    )
