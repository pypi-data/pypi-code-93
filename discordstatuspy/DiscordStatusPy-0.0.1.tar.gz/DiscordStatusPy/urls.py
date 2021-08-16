"""
Sub-module with url constants
"""

__all__ = [
    "SUMMARY_URL",
    "STATUS_URL",
    "COMPONENTS_URL",
    "INCIDENTS_URL",
    "UNRESOLVED_INCIDENTS_URL",
    "MAINTENANCES_URL",
    "UPCOMING_MAINTENANCES_URL",
    "ACTIVE_MAINTENANCES_URL"
]


PAGE = "https://discordstatus.com/"
API = "api/v2/"
JSON = ".json"

SUMMARY = "summary"
STATUS = "status"
COMPONENTS = "components"
INCIDENTS = "Incidents"
UNRESOLVED_INCIDENTS = "incidents/unresolved"
MAINTENANCES = "scheduled-maintenances"
UPCOMING_MAINTENANCES = "scheduled-maintenances/upcoming"
ACTIVE_MAINTENANCES = "scheduled-maintenances/active"

def __build_url(endpoint: str) -> str:
    """
    Joins a url

    IN:
        endpoint - the API endpoint

    OUT:
        API url, string
    """
    return f"{PAGE}{API}{endpoint}{JSON}"

SUMMARY_URL = __build_url(SUMMARY)
STATUS_URL = __build_url(STATUS)
COMPONENTS_URL = __build_url(COMPONENTS)
INCIDENTS_URL = __build_url(INCIDENTS)
UNRESOLVED_INCIDENTS_URL = __build_url(UNRESOLVED_INCIDENTS)
MAINTENANCES_URL = __build_url(MAINTENANCES)
UPCOMING_MAINTENANCES_URL = __build_url(UPCOMING_MAINTENANCES)
ACTIVE_MAINTENANCES_URL = __build_url(ACTIVE_MAINTENANCES)
