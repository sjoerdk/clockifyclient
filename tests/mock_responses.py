"""Cached examples of http responses from Clockify API v1. These partly come
from https://clockify.me/developers-api and party were recorded by interacting
with the server live around november 2019
"""

from tests.factories import RequestMockResponse


# with non-existent API or missing key
AUTH_ERROR = RequestMockResponse(
    '{"description":"Full authentication is required to access this resource","code":1000}',
    401,
)

# Trying to set something
CURRENTLY_RUNNING_ENTRY_NOT_FOUND = RequestMockResponse(
    """{"message":"Currently running time entry doesn't exist on workspace 123456 for user 123456.","code":404}""",
    404,
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
    200,
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
    200,
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
    200,
)

# calling post '/workspaces/<workspace id>/time-entries'
POST_TIME_ENTRY = RequestMockResponse(
    """{"id": "123456", "description": "testing description", "tagIds": null,
 "userId": "123456", "billable": false, "taskId": null, "projectId": "123456",
 "timeInterval": {"start": "2019-10-23T17:18:58Z", "end": null, "duration": null},
 "workspaceId": "123456", "isLocked": false}
 """,
    201,
)
